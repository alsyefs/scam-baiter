import random
from database.sms_table import SmsDatabaseManager
from globals import (
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBERS
)
from logs import LogManager
log = LogManager.get_logger()
import traceback
from twilio.rest import Client

def send_sms(to_number, sms_text):
    sms_from = random.choice(TWILIO_PHONE_NUMBERS)  # set from to a random number from the list of numbers:
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=sms_text,
            from_=sms_from,
            to=to_number
        )
        log.info(f"SMS sent from ({sms_from}) to ({to_number}) with message: ({sms_text}).")
        SmsDatabaseManager.insert_sms(from_sms=sms_from,
                                      to_sms=to_number,
                                      sms_sid=message.sid,
                                      sms_text=sms_text,
                                      sms_recording_url=None,
                                      is_inbound=0,
                                      is_outbound=1,
                                      is_scammer=0)
        return message.sid
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("", traceback.format_exc())
        return "An error occurred: %s" % str(e)