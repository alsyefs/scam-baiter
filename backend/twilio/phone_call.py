import random
from globals import (
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
    TWILIO_CALL_URL, TWILIO_PHONE_NUMBERS
)
from logs import LogManager
log = LogManager.get_logger()
import traceback
from twilio.rest import Client
from database.calls_table import CallsDatabaseManager

def call_number(to_number):
    call_from = random.choice(TWILIO_PHONE_NUMBERS)  # set from to a random number from the list of numbers
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            url=TWILIO_CALL_URL,
            to=to_number,
            from_=call_from
        )
        log.info(f"Call made from ({call_from}) to ({to_number}).")
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
        log.error("An error occurred: %s", str(e))
        log.error("", traceback.format_exc())
        return "An error occurred: %s" % str(e)
