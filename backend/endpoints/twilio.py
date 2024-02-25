import datetime
from flask import Blueprint, request, render_template, send_file, session, redirect, url_for, flash, Response, jsonify
from functools import wraps
from backend.database.models import db_models, User, Role, CallConversations
from logs import LogManager
log = LogManager.get_logger()
import traceback
from twilio.twiml.voice_response import VoiceResponse, Gather, Conversation
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from backend import twilio
from backend.responder.Chatgpt_Replier import gen_text1, gen_text2, gen_text3
from database.sms_table import SmsDatabaseManager
# from backend.elevenlabs.tts_ai import text_to_speech_mp3
from backend.models.tts.tts_openai_model import tts_openai
from backend.responder.phone_call_script import generate_call_response
from globals import (
    TTS_MP3_PATH, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, RESPONSE_SENTENCES
)
import random
import time

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
    
@twilio_bp.route("/make_call", methods=['POST'])
def make_call():
    try:
        to_number = request.json.get('toNumber', None)
        print(f"Calling number: ({to_number})...")
        twilio.call_number(to_number)
        return jsonify({"status": "success", "message": "Call made successfully."})
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)})

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
    
@twilio_bp.route("/ongoing_call", methods=['GET', 'POST'])
def call_handler():
    try:
        response = VoiceResponse()
        # gather = Gather(input='speech', action='/handle_ongoing_call')
        gather = Gather(input='speech dtmf', action='/handle_ongoing_call', timeout=5, profanityFilter=False, speechTimeout=1)
        if 'greeted' not in session:
            log.info(f"Ongoing call started from: ({request.values.get('From', None)}), to: ({request.values.get('To', None)}).")
            session['greeted'] = True
            session['selected_voice_gender'] = random.choice([1, 2])  # 1: male, 2: female
            session['selected_voice_accent'] = random.choice(['us', 'uk'])  # 1: British, 2: American # for tts_openai

            startCall = RESPONSE_SENTENCES["startCall"][random.randint(0, len(RESPONSE_SENTENCES["startCall"])-1)]
            tts_openai(startCall, session['selected_voice_gender'], session['selected_voice_accent'])
            # session['selected_voice_accent'] = random.choice([1, 2])  # 1: British, 2: American
            # session['selected_voice_age'] = random.choice([1, 2, 3])  # 1: young, 2: middle aged, 3: old
            # text_to_speech_mp3("Hello!", session['selected_voice_accent'], session['selected_voice_gender'], session['selected_voice_age'])
            gather.play('/tts_play')
            # response.record(action='/recording_status', method='POST', maxLength=3600, timeout=15)
            # tts_openai("uh huh", session['selected_voice_gender'], session['selected_voice_accent'])
            # gather.play('/tts_play')
        
        # response.record(action='/recording_status', method='POST', maxLength=3600, timeout=15)
        
        # recording = response.record(action='/recording_status', method='POST', maxLength=3600, timeout=15)
        # response.enqueue(recording)
        response.append(gather)
        return Response(str(response), mimetype='text/xml')
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)
    
@twilio_bp.route("/tts_play", methods=['GET', 'POST'])
def tts_play():
    try:
        return send_file(TTS_MP3_PATH)
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)

@twilio_bp.route("/handle_ongoing_call", methods=['GET', 'POST'])
def handle_ongoing_call():
    print("STARTED /handle_ongoing_call")
    start_time = time.time()
    received_voice_text_input = request.values.get('SpeechResult', None)
    time_to_receive_text_input = time.time() - start_time
    time_to_receive_text_input = f"{time_to_receive_text_input:.2f} seconds" if time_to_receive_text_input < 60 else f"{time_to_receive_text_input/60:.2f} minutes"
    print(f"Received voice input in ({time_to_receive_text_input}).")
    # time_to_recognize = request.values.get('RecognitionTime', None)
    response = VoiceResponse()
    # response.record(action='/recording_status', method='POST', maxLength=3600, timeout=15)
    generated_response = ''
    if received_voice_text_input.lower() == 'end call':
        tts_openai("Ending call now. Goodbye!", session['selected_voice_gender'], session['selected_voice_accent'])
        # text_to_speech_mp3("Ending call now. Goodbye!", session['selected_voice_accent'], session['selected_voice_gender'], session['selected_voice_age'])
        response.play('/tts_play')
        log.info(f"Call from:({request.values.get('From', None)}), to:({request.values.get('To', None)}). Received voice input: ({received_voice_text_input}). Ending call with the command: (end call).")
    elif received_voice_text_input:
        # generated_response = gen_text3(received_voice_text_input)
        generated_response = generate_call_response(received_voice_text_input)
        time_to_generate_text_response = time.time() - start_time
        time_to_generate_text_response = f"{time_to_generate_text_response:.2f} seconds" if time_to_generate_text_response < 60 else f"{time_to_generate_text_response/60:.2f} minutes"
        print(f"Generated text response in ({time_to_generate_text_response}).")
        tts_openai(generated_response, session['selected_voice_gender'], session['selected_voice_accent'])
        time_to_generate_voice_response = time.time() - start_time
        time_to_generate_voice_response = f"{time_to_generate_voice_response:.2f} seconds" if time_to_generate_voice_response < 60 else f"{time_to_generate_voice_response/60:.2f} minutes"
        print(f"Generated voice response in ({time_to_generate_voice_response}).")
        # text_to_speech_mp3(generated_response, session['selected_voice_accent'], session['selected_voice_gender'], session['selected_voice_age'])
        response.play('/tts_play')
        completed_time = time.time() - start_time
        completed_time = f"{completed_time:.2f} seconds" if completed_time < 60 else f"{completed_time/60:.2f} minutes"
        print(f"ENDED /handle_ongoing_call. Call handling completed in ({completed_time}).")
        log.info(f"Call from:({request.values.get('From', None)}), to:({request.values.get('To', None)}). Received voice input: ({received_voice_text_input}). Generated voice response: ({generated_response}).")
        response.redirect('/ongoing_call')
    else:
        tts_openai("Sorry, I did not catch that. Please try again.", session['selected_voice_gender'], session['selected_voice_accent'])
        # text_to_speech_mp3("Sorry, I did not catch that. Please try again.", session['selected_voice_accent'], session['selected_voice_gender'], session['selected_voice_age'])
        response.play('/tts_play')
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

    # Store the recording URL in your database
    # CallsDatabaseManager.update_call_recording_url(recording_sid, recording_url)
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
        tts_openai("Goodbye!", session['selected_voice_gender'], session['selected_voice_accent'])
        resp.play('/tts_play')
        resp.hangup()
        log.info(f"Call ended from: ({request.values.get('From', None)}), to: ({request.values.get('To', None)}).")
        return Response(str(resp), mimetype='text/xml')
    except Exception as e:
        log.error(f"An error occurred: {str(e)} traceback: {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)