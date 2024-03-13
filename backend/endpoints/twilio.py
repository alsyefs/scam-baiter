import base64
import datetime
import json
from flask import Blueprint, request, render_template, send_file, session, redirect, url_for, flash, Response, jsonify, send_from_directory
from socketio_instance import socketio, sock
from functools import wraps
from backend.database.models import db_models, User, Role, CallConversations
from logs import LogManager
log = LogManager.get_logger()
import traceback
from twilio.twiml.voice_response import VoiceResponse, Gather, Conversation, Start, Connect, Stream
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from backend import twilio
from backend.responder.Chatgpt_Replier import gen_text1, gen_text2, gen_text3, gen_text3_async
from database.sms_table import SmsDatabaseManager
# from backend.elevenlabs.tts_ai import text_to_speech_mp3
from backend.models.tts.tts_openai_model import tts_openai, tts_openai_audio
from backend.models.tts.tts_openai_async_model import tts_openai_async
from backend.models.tts.stt_openai_model import stt_openai_decoded_audio, stt_openai_audio_file
from backend.models.tts.twilio_transcriber import TwilioTranscriber
from responder.phone_call_script_logic import generate_call_response
from globals import (
    TTS_MP3_PATH, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, DOMAIN_NAME,
    STT_MP3_PATH, FINAL_TRANSCRIPTIONS, TTS_WAV_PATH
)
import random
import time
from responder import phone_call_script_data
import asyncio

speaker_voice = 'Polly.Matthew-Neural'
selected_voice_accent = 1
selected_voice_gender = 1
selected_voice_age = 2

twilio_bp = Blueprint('twilio', __name__)

def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                flash('You need to be signed in to view this page.', 'error')
                log.warning("User not signed in. Redirecting to sign in page (twilio).")
                return redirect(url_for('users.signin'))
            current_user = User.query.filter_by(username=session['username']).first()
            if current_user:
                user_roles = [role.name for role in current_user.roles]
                if any(role in roles for role in user_roles):
                    return f(*args, **kwargs)
            flash('You do not have the required permissions to view this page.', 'error')
            log.warning(f"User ({session['username']}) does not have the required permissions to view this page (/twilio).")
            return redirect(url_for('index'))
        return decorated_function
    return wrapper
@twilio_bp.route('/twilio')
@requires_roles('admin', 'super admin')
def index():
    user_roles = []
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            user_roles = [role.name for role in user.roles]
    return render_template('twilio.html', user_roles=user_roles)
@twilio_bp.route("/twilio_errors", methods=['GET', 'POST'])
def twilio_errors():
    try:
        # Expect the following payload to be sent from Twilio in this webhook endpoint:
        # AccountSid: Unique identifier of the account that generated the Debugger event.
        # Sid: Unique identifier of this Debugger event.
        # ParentAccountSid: Unique identifier of the parent account. This parameter only exists if the above account is a subaccount.
        # Timestamp: Time of occurrence of the Debugger event.
        # Level: Severity of the Debugger event. Possible values are Error and Warning.
        # PayloadType: application/json
        # Payload: JSON data specific to the Debugger Event.
        account_sid = request.values.get('AccountSid', None)
        sid = request.values.get('Sid', None)
        parent_account_sid = request.values.get('ParentAccountSid', None)
        timestamp = request.values.get('Timestamp', None)
        level = request.values.get('Level', None)
        payload_type = request.values.get('PayloadType', None)
        payload = request.values.get('Payload', None)
        error_message = f"Twilio error: AccountSid: ({account_sid}), Sid: ({sid}), ParentAccountSid: ({parent_account_sid}), Timestamp: ({timestamp}), Level: ({level}), PayloadType: ({payload_type}), Payload: ({payload})."
        log.error(error_message)
        return "Twilio error message: %s" % str(error_message)
    except Exception as e:
        log.error(f"An error occurred: {str(e)}. traceback: {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)
@twilio_bp.route("/incoming_sms", methods=['GET', 'POST'])
def incoming_sms():
    try:
        incoming_message = request.values.get('Body', None)
        sms_id = request.values.get('SmsSid', None)
        log.info(f"Incoming SMS from: ({request.values.get('From', None)}), to: ({request.values.get('To', None)}), incoming message: ({incoming_message}).")
        SmsDatabaseManager.insert_sms(from_sms=request.values.get('From', None),
                                      to_sms=request.values.get('To', None),
                                      sms_sid=sms_id,
                                      sms_text=incoming_message,
                                      sms_recording_url=None,
                                      is_inbound=1,
                                      is_outbound=0,
                                      is_scammer=0)
        resp = MessagingResponse()
        generated_response = gen_text3(incoming_message)
        log.info(f"Generated SMS response from:({request.values.get('To', None)}), to:({request.values.get('From', None)}), response message: ({generated_response}).")
        message = request.args.get('message', generated_response)
        SmsDatabaseManager.insert_sms(from_sms=request.values.get('To', None),
                                      to_sms=request.values.get('From', None),
                                      sms_sid=sms_id,
                                      sms_text=generated_response,
                                      sms_recording_url=None,
                                      is_inbound=0,
                                      is_outbound=1,
                                      is_scammer=0)
        resp.message(message)
        return str(resp)
    except Exception as e:
        log.error(f"An error occurred: {str(e)}. traceback: {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)
@twilio_bp.route("/send_sms", methods=['POST'])
def send_sms():
    try:
        to_number = request.json.get('toNumber', None)
        smsText = request.json.get('smsText', None)
        result = twilio.send_sms(to_number, smsText)
        return jsonify(result)
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)})
@twilio_bp.route("/incoming_sms_failed", methods=['POST'])
def incoming_sms_failed():
    try:
        log.error(f"Incoming SMS failed from: ({request.values.get('From', None)}), to: ({request.values.get('To', None)}).")
        return "Incoming SMS failed."
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)

# set up a route to handle incoming calls and direct them to the call handler:
@twilio_bp.route("/incoming_call", methods=['GET', 'POST'])
def incoming_call():
    try:
        response = VoiceResponse()
        # session['selected_voice_gender'] = random.choice([1, 2])  # 1: male, 2: female
        # session['selected_voice_accent'] = random.choice(['us', 'uk'])  # 1: British, 2: American # for tts_openai
        # tts_openai("I am sorry, but the person your calling is not available right now. Please leave your message after the beep. Thank you!", session['selected_voice_gender'], session['selected_voice_accent'])
        # gather = Gather(input='speech dtmf', timeout=5, profanityFilter=False, speechTimeout=1)
        # gather.play('/tts_play')
        response.say("I am sorry, but the person your calling is not available right now. Please leave your message after the beep. Thank you!")
        response.record(action='/recording_status', method='POST', maxLength=3600, timeout=15) # Remove to complete the call.
        # response.redirect('/ongoing_call') # This is if we want to continue the call instead of the voicemail.
        return Response(str(response), mimetype='text/xml')
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)

############## Synchronous call handling: ##############
@twilio_bp.route("/make_call_synchronous", methods=['POST'])
def make_call_synchronous():
    try:
        to_number = request.json.get('toNumber', None)
        print(f"Calling number: ({to_number})...")
        twilio.call_number_synchronous(to_number)
        return jsonify({"status": "success", "message": "Call made successfully."})
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)})

def get_openai_voice(gender, accent):
    voices = ["nova", "shimmer", "echo", "onyx", "fable", "alloy"]
    if gender == 1 and accent == "us":
        voices = ["echo", "onyx"]
    elif gender == 1 and accent == "uk":
        voices = ["fable"]
    elif gender == 2 and accent == "us":
        voices = ["alloy", "nova", "shimmer"]
    else:
        voices = ["alloy"]
    voice = random.choice(voices)
    return voice

@twilio_bp.route("/ongoing_call_synchronous", methods=['GET', 'POST'])
def ongoing_call_synchronous():
    try:
        response = VoiceResponse()
        gather = Gather(input='speech', action='/handle_ongoing_call_synchronous', timeout=5, profanityFilter=False, speechTimeout=5)
        if 'greeted' not in session:
            print("Starting call with greeting...")
            log.info(f"Ongoing call started from: ({request.values.get('From', None)}), to: ({request.values.get('To', None)}).")
            session['greeted'] = True
            session['selected_voice_gender'] = random.choice([1, 2])  # 1: male, 2: female
            session['selected_voice_accent'] = random.choice(['us', 'uk'])  # 1: British, 2: American # for tts_openai
            session['selected_voice'] = get_openai_voice(session['selected_voice_gender'], session['selected_voice_accent'])
            # # Using a static script
            # RESPONSE_SENTENCES = phone_call_script_data.get_response_sentence("startCall")
            # start_call = RESPONSE_SENTENCES["startCall"][random.randint(0, len(RESPONSE_SENTENCES["startCall"])-1)]
            # session['selected_voice_accent'] = random.choice([1, 2])  # 1: British, 2: American
            # session['selected_voice_age'] = random.choice([1, 2, 3])  # 1: young, 2: middle aged, 3: old
            # text_to_speech_mp3("Hello!", session['selected_voice_accent'], session['selected_voice_gender'], session['selected_voice_age'])
            # response.record(action='/recording_status', method='POST', maxLength=3600, timeout=15)
            # tts_openai("uh huh", session['selected_voice_gender'], session['selected_voice_accent'])
            start_call = "Hello there! Is this a good time to talk?"
            tts_openai(start_call, session['selected_voice'])
            gather.play('/tts_play_synchronous')
        # response.record(action='/recording_status', method='POST', maxLength=3600, timeout=15)
        # recording = response.record(action='/recording_status', method='POST', maxLength=3600, timeout=15)
        # response.enqueue(recording)
        response.append(gather)
        return Response(str(response), mimetype='text/xml')
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)

@twilio_bp.route("/handle_ongoing_call_synchronous", methods=['GET', 'POST'])
def handle_ongoing_call_synchronous():
    print("STARTED /handle_ongoing_call_synchronous")
    received_voice_text_input = request.values.get('SpeechResult', None)
    start_time = time.time()
    time_to_receive_text_input = time.time() - start_time
    time_to_receive_text_input = f"{time_to_receive_text_input:.2f} seconds" if time_to_receive_text_input < 60 else f"{time_to_receive_text_input/60:.2f} minutes"
    print(f"Received voice input in ({time_to_receive_text_input}).")
    # time_to_recognize = request.values.get('RecognitionTime', None)
    response = VoiceResponse()
    # response.record(action='/recording_status', method='POST', maxLength=3600, timeout=15)
    generated_response = ''
    if received_voice_text_input.lower() == 'end call':
        tts_openai("Ending call now. Goodbye!", session['selected_voice'])
        # text_to_speech_mp3("Ending call now. Goodbye!", session['selected_voice_accent'], session['selected_voice_gender'], session['selected_voice_age'])
        response.play('/tts_play_synchronous')
        log.info(f"Call from:({request.values.get('From', None)}), to:({request.values.get('To', None)}). Received voice input: ({received_voice_text_input}). Ending call with the command: (end call).")
    elif received_voice_text_input:
        generated_response = gen_text3(received_voice_text_input)
        # generated_response = generate_call_response(received_voice_text_input)
        time_to_generate_text_response = time.time() - start_time
        time_to_generate_text_response = f"{time_to_generate_text_response:.2f} seconds" if time_to_generate_text_response < 60 else f"{time_to_generate_text_response/60:.2f} minutes"
        print(f"Generated text response in ({time_to_generate_text_response}).")
        tts_openai(generated_response, session['selected_voice'])
        time_to_generate_voice_response = time.time() - start_time
        time_to_generate_voice_response = f"{time_to_generate_voice_response:.2f} seconds" if time_to_generate_voice_response < 60 else f"{time_to_generate_voice_response/60:.2f} minutes"
        print(f"Generated voice response in ({time_to_generate_voice_response}).")
        # text_to_speech_mp3(generated_response, session['selected_voice_accent'], session['selected_voice_gender'], session['selected_voice_age'])
        response.play('/tts_play_synchronous')
        completed_time = time.time() - start_time
        completed_time = f"{completed_time:.2f} seconds" if completed_time < 60 else f"{completed_time/60:.2f} minutes"
        print(f"ENDED /handle_ongoing_call_synchronous. Call handling completed in ({completed_time}).")
        log.info(f"Call from:({request.values.get('From', None)}), to:({request.values.get('To', None)}). Received voice input: ({received_voice_text_input}). Generated voice response: ({generated_response}).")
        response.redirect('/ongoing_call_synchronous')
    else:
        tts_openai("Sorry, I did not catch that. Please try again.", session['selected_voice'])
        # text_to_speech_mp3("Sorry, I did not catch that. Please try again.", session['selected_voice_accent'], session['selected_voice_gender'], session['selected_voice_age'])
        response.play('/tts_play_synchronous')
        log.info(f"Call from:({request.values.get('From', None)}), to:({request.values.get('To', None)}). Caller did not say anything.")
    new_call_conversation = CallConversations(
                from_number=request.values.get('From', None),
                to_number=request.values.get('To', None),
                caller_text=received_voice_text_input,
                system_text=generated_response,
                call_sid=request.values.get('CallSid', None),
                call_status=request.values.get('CallStatus', None),
            )
    db_models.session.add(new_call_conversation)
    db_models.session.commit()
    return Response(str(response), mimetype='text/xml')

@twilio_bp.route("/tts_play_synchronous", methods=['GET', 'POST'])
def tts_play_synchronous():
    try:
        print("Playing TTS...")
        return send_file(TTS_WAV_PATH)
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)

@twilio_bp.route("/ongoing_call_failed", methods=['POST'])
def ongoing_call_failed():
    try:
        log.error(f"Ongoing call failed from: ({request.values.get('From', None)}), to: ({request.values.get('To', None)}).")
        return "Ongoing call failed."
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)

@twilio_bp.route("/recording_status", methods=['POST'])
def recording_status():
    recording_sid = request.values.get('RecordingSid', None)
    recording_url = request.values.get('RecordingUrl', None)
    recording_duration = request.values.get('RecordingDuration', None)
    recording_status = request.values.get('RecordingStatus', None)
    new_call_conversation = CallConversations(
                from_number=request.values.get('From', None),
                to_number=request.values.get('To', None),
                caller_text="Recording...",
                system_text="Recording...",
                call_sid= recording_sid, # request.values.get('CallSid', None),
                call_status=recording_status, # request.values.get('CallStatus', None),
                call_duration=recording_duration,
                recording_url=recording_url
            )
    db_models.session.add(new_call_conversation)
    db_models.session.commit()
    return "OK"

@twilio_bp.route("/get_all_recordings", methods=['GET'])
def get_all_recordings():
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        recordings = client.recordings.list(limit=20) # Change the limit to get more recordings
        for record in recordings:
            print(record.sid)
            print(record.call_sid)
            print(record.duration)
            print(record.date_created)
            print(record.price)
            print(record.uri)
        return render_template('all_recordings.html', recordings=recordings)
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)

def hangup():
    try:
        resp = VoiceResponse()
        tts_openai("Goodbye!", session['selected_voice'])
        resp.play('/tts_play')
        resp.hangup()
        log.info(f"Call ended from: ({request.values.get('From', None)}), to: ({request.values.get('To', None)}).")
        return Response(str(resp), mimetype='text/xml')
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)

############## Asynchronous call handling: ##############
@twilio_bp.route("/make_call_asynchronous", methods=['POST'])
async def make_call_asynchronous():
    try:
        to_number = request.json.get('toNumber', None)
        print(f"Calling number: ({to_number})...")
        await twilio.call_number_asynchronous(to_number)
        return jsonify({"status": "success", "message": "Call made successfully."})
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)})

async def get_openai_voice_async(gender, accent):
    voices = ["nova", "shimmer", "echo", "onyx", "fable", "alloy"]
    if gender == 1 and accent == "us":
        voices = ["echo", "onyx"]
    elif gender == 1 and accent == "uk":
        voices = ["fable"]
    elif gender == 2 and accent == "us":
        voices = ["alloy", "nova", "shimmer"]
    else:
        voices = ["alloy"]
    voice = random.choice(voices)
    return voice

__received_voice_text_input = ""
__generated_voice_text_response = ""
@twilio_bp.route("/ongoing_call_asynchronous", methods=['GET', 'POST'])
async def ongoing_call_asynchronous():
    global __received_voice_text_input
    global __generated_voice_text_response
    try:
        response = VoiceResponse()
        gather = Gather(input='speech dtmf', timeout=5, profanityFilter=False, speechTimeout=5, partial_result_callback='/partial_result_callback')
        if 'greeted' not in session:
            print("Starting call with greeting...")
            log.info(f"Async ongoing call started from: ({request.values.get('From', None)}), to: ({request.values.get('To', None)}).")
            session['greeted'] = True
            session['selected_voice_gender'] = random.choice([1, 2])  # 1: male, 2: female
            session['selected_voice_accent'] = random.choice(['us', 'uk'])  # 1: British, 2: American # for tts_openai
            session['selected_voice'] = await get_openai_voice_async(session['selected_voice_gender'], session['selected_voice_accent'])
            start_call = "Hello there! Is this a good time to talk?"
            tts_openai_async(start_call, session['selected_voice'])
            gather.play('/tts_play_async')
        else:
            print("Continuing call, already greeted...")
            if __generated_voice_text_response:
                # tts_openai(__generated_voice_text_response, session['selected_voice_gender'], session['selected_voice_accent'])
                tts_openai_async(__generated_voice_text_response, session['selected_voice'])
                response.play('/tts_play_async')
                __received_voice_text_input = ""
                __generated_voice_text_response = ""
        # response.record(action='/recording_status', method='POST', maxLength=3600, timeout=15)
        # recording = response.record(action='/recording_status', method='POST', maxLength=3600, timeout=15)
        # response.enqueue(recording)
        response.append(gather)
        return Response(str(response), mimetype='text/xml')
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)

@twilio_bp.route("/partial_result_callback", methods=['POST'])
async def partial_result_callback():
    start_time = time.time()
    global __generated_voice_text_response
    global __received_voice_text_input
    response = VoiceResponse()
    try:
        partial_transcription = request.form.get('UnstableSpeechResult', '') # call_sid = request.form.get('CallSid', '')
        if partial_transcription and len(partial_transcription.split()) >= 3:
            __received_voice_text_input = partial_transcription
            __generated_voice_text_response = asyncio.run(gen_text3_async(__received_voice_text_input))
            # __generated_voice_text_response = generate_call_response(__received_voice_text_input)
            print(f"prompt: ({__received_voice_text_input}), response: ({__generated_voice_text_response}).")
            completed_time = time.time() - start_time
            completed_time = f"{completed_time:.2f} seconds" if completed_time < 60 else f"{completed_time/60:.2f} minutes"
            print(f"ENDED /partial_result_callback. Call handling completed in ({completed_time}).")
            response.redirect(url_for('twilio.ongoing_call_asynchronous'))
        elif not partial_transcription:
            __generated_voice_text_response = asyncio.run(gen_text3_async(__received_voice_text_input))
            response.redirect(url_for('twilio.ongoing_call_asynchronous'))
        else:
            __received_voice_text_input = ""
            __generated_voice_text_response = ""
            print(f"({partial_transcription}).")
            response.redirect('/partial_result_callback')
        return Response(str(response), mimetype='text/xml')
    except Exception as e:
        log.error(f"Error handling partial result callback: {str(e)}")
    return Response("An error occurred", status=500)
# old, works!
# @twilio_bp.route("/partial_result_callback", methods=['POST'])
# def partial_result_callback():
#     start_time = time.time()
#     global __generated_voice_text_response
#     global __received_voice_text_input
#     response = VoiceResponse()
#     try:
#         if __generated_voice_text_response:
#             response.redirect('/partial_result_callback')
#         partial_transcription = request.form.get('UnstableSpeechResult', '') # call_sid = request.form.get('CallSid', '')
#         if partial_transcription:
#             __received_voice_text_input = partial_transcription
#             if len(__received_voice_text_input.split()) > 3:
#                 # __generated_voice_text_response = gen_text3(__received_voice_text_input)
#                 __generated_voice_text_response = asyncio.run(gen_text3_async(__received_voice_text_input))
#                 # __generated_voice_text_response = generate_call_response(__received_voice_text_input)
#                 print(f"prompt length: ({len(__received_voice_text_input.split())}).")
#                 print(f"prompt: ({__received_voice_text_input}), response: ({__generated_voice_text_response}).")
#                 completed_time = time.time() - start_time
#                 completed_time = f"{completed_time:.2f} seconds" if completed_time < 60 else f"{completed_time/60:.2f} minutes"
#                 print(f"ENDED /partial_result_callback. Call handling completed in ({completed_time}).")
#                 # response.redirect('/partial_result_callback')
#                 response.redirect(url_for('twilio.ongoing_call_asynchronous'))
#         if not partial_transcription and __received_voice_text_input:
#             # __generated_voice_text_response = gen_text3(__received_voice_text_input)
#             __generated_voice_text_response = asyncio.run(gen_text3_async(__received_voice_text_input))
#             # __generated_voice_text_response = generate_call_response(__received_voice_text_input)
#             print(f"prompt: ({__received_voice_text_input}), response: ({__generated_voice_text_response}).")
#             completed_time = time.time() - start_time
#             completed_time = f"{completed_time:.2f} seconds" if completed_time < 60 else f"{completed_time/60:.2f} minutes"
#             print(f"ENDED /partial_result_callback. Call handling completed in ({completed_time}).")
#             response.redirect(url_for('twilio.ongoing_call_asynchronous'))
#             # response.redirect('/partial_result_callback')
#         return Response(str(response), mimetype='text/xml')
#     except Exception as e:
#         log.error(f"Error handling partial result callback: {str(e)}")
#     return Response("An error occurred", status=500)

############## Socket call handling: ##############
@twilio_bp.route("/make_call_socket", methods=['POST'])
async def make_call_socket():
    try:
        to_number = request.json.get('toNumber', None)
        print(f"Calling number: ({to_number})...")
        await twilio.call_number_socket(to_number)
        return jsonify({"status": "success", "message": "Call made successfully."})
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)})

@twilio_bp.route("/ongoing_call_socket", methods=['GET', 'POST'])
def ongoing_call_socket():
    print("STARTED /ongoing_call")
    try:
        socket_connection = f"wss://{DOMAIN_NAME}/realtime_call_socket"
        session['selected_voice_gender'] = random.choice([1, 2])  # 1: male, 2: female
        session['selected_voice_accent'] = random.choice(['us', 'uk'])  # 1: British, 2: American # for tts_openai
        session['selected_voice'] = get_openai_voice(session['selected_voice_gender'], session['selected_voice_accent'])
        start_call = "Hello there! Is this a good time to talk?"
        tts_openai(start_call, session['selected_voice'])
        xml = f"""
<Response>
    <Play>https://{DOMAIN_NAME}/tts_play_synchronous</Play>
    <Connect><Stream url='{socket_connection}' /></Connect>
</Response>
""".strip()
        return Response(xml, mimetype='text/xml')
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)

@twilio_bp.route('/get_final_transcripts')
def get_final_transcripts():
    return jsonify({"transcripts": FINAL_TRANSCRIPTIONS})

processing_final_transcriptions = False
@sock.route('/realtime_call_socket')
def realtime_call_socket(ws):
    global processing_final_transcriptions
    transcriber = None
    stream_sid = None
    stream_connected = None
    stream_start = None
    stream_stop = None
    while True:
        data = json.loads(ws.receive())
        match data['event']:
            case "connected":
                transcriber = TwilioTranscriber()
                transcriber.connect()
                print('transcriber connected')
                stream_connected = time.time()
            case "start":
                stream_sid = data["streamSid"]
                print(f"twilio stream started with stream_sid: {stream_sid}")
                stream_start = time.time()
            case "media": 
                if not processing_final_transcriptions and not FINAL_TRANSCRIPTIONS:
                    payload_b64 = data['media']['payload']
                    payload_mulaw = base64.b64decode(payload_b64)
                    transcriber.stream(payload_mulaw)
                else:
                    start_time = time.time()
                    print("Processing final transcriptions...")
                    time_to_receive_text_input = time.time() - start_time
                    time_to_receive_text_input = f"{time_to_receive_text_input:.2f} seconds" if time_to_receive_text_input < 60 else f"{time_to_receive_text_input/60:.2f} minutes"
                    print(f"Transcribted prompt ({time_to_receive_text_input}): {FINAL_TRANSCRIPTIONS}")
                    generated_response = gen_text3(FINAL_TRANSCRIPTIONS[-1])
                    time_to_generate_text_response = time.time() - start_time
                    print(f"Generated response ({time_to_generate_text_response}): {generated_response}")
                    FINAL_TRANSCRIPTIONS.clear()
                    ws.send(json.dumps({"event": "media", "streamSid": stream_sid, "media": {"payload": tts_openai_audio(generated_response)}}))
                    time_to_generate_voice_response = time.time() - start_time
                    print(f"Audio response sent ({time_to_generate_voice_response}).")
                    pass
            case "stop":
                transcriber.close()
                stream_stop = time.time() - stream_start
                print(f'twilio stream stopped ({stream_stop}).')

# @sock.route('/realtime_call_socket')
# def realtime_call_socket(ws):
#     log.info("Connection accepted")
#     has_seen_media = False # A lot of messages will be sent rapidly. We'll stop showing after the first one.
#     message_count = 0
#     while True:
#         message = ws.receive()
#         if message is None:
#             log.info("No message received...")
#             continue
#         data = json.loads(message) # Messages are a JSON encoded string
#         # Using the event type you can determine what type of message you are receiving
#         if data['event'] == "connected":
#             transcriber = TwilioTranscriber()
#             transcriber.connect()
#             print('transcriber connected')
#         if data['event'] == "start":
#             print('twilio started')
#         if data['event'] == "media":
#             if not has_seen_media:
#                 payload_b64 = data['media']['payload']
#                 payload_mulaw = base64.b64decode(payload_b64)
#                 transcriber.stream(payload_mulaw)

#                 # log.info("Media message: {}".format(message))
#                 # payload = data['media']['payload']
#                 # log.info("Payload is: {}".format(payload))
#                 # chunk = base64.b64decode(payload)
#                 # log.info("That's {} bytes".format(len(chunk)))
#                 # log.info("Additional media messages from WebSocket are being suppressed....")
#                 # stt_openai_decoded_audio(chunk)
#                 # # chunk.stream_to_file(STT_MP3_PATH)
#                 # # response_text = stt_openai(STT_MP3_PATH)
#                 # # tts_openai(response_text, session['selected_voice'])
#                 has_seen_media = True
#         if data['event'] == "closed":
#             print('twilio stopped')
#             transcriber.close()
#             print('transcriber closed')
#             # log.info("Closed Message received: {}".format(message))
#             # break
#         message_count += 1
#     log.info("Connection closed. Received a total of {} messages".format(message_count))
    
# Hit this endpoint to trigger TTS
@twilio_bp.route("/trigger_tts", methods=['GET', 'POST'])
async def trigger_tts_handler():
    text = "Hello there! Is this a good time to talk?"
    print("STARTED /trigger_tts")
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            print("Event loop is already running.")
            loop.create_task(handle_tts_play_async(text))
            print("New task created.")
            loop.run_until_complete(handle_tts_play_async(text))
            print("Running new task...")
        else:
            print("Event loop is not running.")
            loop.run_until_complete(handle_tts_play_async(text))
            print("Running new task...")
            loop.close()
            print("New task completed.")
    except Exception as e:
        print(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
    print("ENDED /trigger_tts")
    return jsonify({"message": "TTS triggered"})

async def handle_tts_play_async(text):
    print("STARTED handle_tts_play_async(text)")
    print(f"Received text: {text}")
    audio_io = await tts_openai_async(text)
    if audio_io:
        # print(f"audio_io: ({audio_io}).")
        # emit('audio_response', {'audio_data': audio_io})
        # socketio.emit('audio_response', {'audio_data': audio_io}, namespace='/')
        print("TTS processing complete")
    else:
        print("Failed to generate TTS")
    print("ENDED handle_tts_play_async(text)")

@twilio_bp.route("/tts_play_async", methods=['GET', 'POST'])
async def tts_play_async():
    global __received_voice_text_input
    global __generated_voice_text_response
    try:
        print("Playing TTS...")
        print(f"Generated voice response: ({__generated_voice_text_response}).")
        if __generated_voice_text_response:
                audio_io = await tts_openai_async(__generated_voice_text_response)
        else:
                audio_io = await tts_openai_async("Hello there! Is this a good time to talk?")
        if audio_io:
            audio_io.seek(0)
            return send_file(audio_io, mimetype='audio/mpeg')
        else:
            return "Failed to generate TTS", 500
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)