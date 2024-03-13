import random
from globals import (
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_CALL_URL_SYNCHRONOUS,
    TWILIO_CALL_URL_ASYNCHRONOUS, TWILIO_PHONE_NUMBERS, TWILIO_CALL_URL_SOCKET,
    TWILIO_RECORDING_STATUS_CALLBACK_URL, TWILIO_PARTIAL_RESULT_CALLBACK_URL
)
from logs import LogManager
log = LogManager.get_logger()
import traceback
from twilio.rest import Client
from database.calls_table import CallsDatabaseManager
def call_number_synchronous(to_number):
    call_from = random.choice(TWILIO_PHONE_NUMBERS)  # set 'call_from' to a random number from the list of numbers
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            url=TWILIO_CALL_URL_SYNCHRONOUS,
            to=to_number,
            from_=call_from,
            record=True,
            recording_status_callback=TWILIO_RECORDING_STATUS_CALLBACK_URL
        )
        log.info(f"Synchronous call request made from ({call_from}) to ({to_number}).")
        CallsDatabaseManager.insert_call(from_call=call_from,
                                         to_call=to_number,
                                         call_sid=call.sid,
                                         call_length=0,
                                         call_recording_url=None,
                                         is_inbound=0,
                                         is_outbound=1,
                                         is_scammer=0)
        return call.sid
    except Exception as e:
        log.error(f"An error occurred: {str(e)}. {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)

async def call_number_asynchronous(to_number):
    call_from = random.choice(TWILIO_PHONE_NUMBERS)  # set 'call_from' to a random number from the list of numbers
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            url=TWILIO_CALL_URL_ASYNCHRONOUS,
            to=to_number,
            from_=call_from,
            record=True,
            recording_status_callback=TWILIO_RECORDING_STATUS_CALLBACK_URL
        )
        log.info(f"Asynchronous call request made from ({call_from}) to ({to_number}).")
        CallsDatabaseManager.insert_call(from_call=call_from,
                                         to_call=to_number,
                                         call_sid=call.sid,
                                         call_length=0,
                                         call_recording_url=None,
                                         is_inbound=0,
                                         is_outbound=1,
                                         is_scammer=0)
        return call.sid
    except Exception as e:
        log.error(f"An error occurred: {str(e)}. {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)
    
async def call_number_socket(to_number):
    call_from = random.choice(TWILIO_PHONE_NUMBERS)  # set 'call_from' to a random number from the list of numbers
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            url=TWILIO_CALL_URL_SOCKET,
            to=to_number,
            from_=call_from,
            record=True,
            recording_status_callback=TWILIO_RECORDING_STATUS_CALLBACK_URL
        )
        log.info(f"Socket call request made from ({call_from}) to ({to_number}).")
        CallsDatabaseManager.insert_call(from_call=call_from,
                                         to_call=to_number,
                                         call_sid=call.sid,
                                         call_length=0,
                                         call_recording_url=None,
                                         is_inbound=0,
                                         is_outbound=1,
                                         is_scammer=0)
        return call.sid
    except Exception as e:
        log.error(f"An error occurred: {str(e)}. {traceback.format_exc()}")
        return "An error occurred: %s" % str(e)