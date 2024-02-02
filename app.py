import os
from sarufi import Sarufi
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response


# Load environment variables
load_dotenv()

# Initialize Sarufi and get the bot
sarufi = Sarufi(api_key=os.getenv("SARUFI_API_KEY"))
sarufi_bot = sarufi.get_bot(os.getenv("SARUFI_BOT_ID"))

app = FastAPI()


@app.post("/voicemail")
async def voicemail(request: Request):
    """
    Handle incoming voice call requests.

    Parameters:
    - request: FastAPI Request object containing the incoming call data.

    Returns:
    - FastAPI Response object with appropriate XML response.
    """
    try:
        form_data = await request.form()
        session_id = form_data.get("sessionId")
        call_number = form_data.get("callerNumber") 
        is_active = int(form_data.get("isActive"))
        dtfm_digits = form_data.get("dtmfDigits", None)
        sarufi_chat_id = f'{call_number}-{session_id}'
        if dtfm_digits:
            dtfm_digits = int(dtfm_digits.strip())

        if is_active == 1:
            # If the call is active, respond with a message and play an audio file
            sarufi_response = (
                sarufi_bot.respond("start", chat_id=sarufi_chat_id)
                if not dtfm_digits
                else sarufi_bot.respond(dtfm_digits, chat_id=sarufi_chat_id)
            )
            s_response = ".".join(sarufi_response.get("message"))
            next_state = sarufi_response.get("next_state")

            if s_response:
                sarufi_response = "Please listen to our awesome record"
                if next_state != "end":
                    response = VoiceResponse.get_digits(s_response)
                else:
                    response = VoiceResponse.say(s_response)
            else:
                response = VoiceResponse.say(sarufi_response)

            template = """<?xml version="1.0" encoding="UTF-8"?>
                        <Response>
                        {response}
                        </Response>"""
            response = template.format(response=response)
            return Response(content=response, media_type="application/xml")

        else:
            # If the call is not active, read in call details
            duration = form_data["durationInSeconds"]
            currency_code = form_data["currencyCode"]
            amount = form_data["amount"]
            print("Call duration is {} seconds".format(duration))
            print("The currency code is {}".format(currency_code))
            print("The amount received is {}".format(amount))
            print("The session ID is {}".format(session_id))
            print("The call has ended")

            # You can store this information in the database for your records
            return ""
    except Exception as e:
        # Log any unexpected exceptions and return an error response
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")




class VoiceResponse:
    """
    Class to handle voice response.
    """

    @staticmethod
    def say(response):
        return f"<Say>{response}</Say>"

    @staticmethod
    def play(response):
        return f"<Play>{response}</Play>"

    @staticmethod
    def get_digits(response, timeout=20, finishOnKey="#"):
        return f"""
                <GetDigits timeout="{timeout}" finishOnKey="{finishOnKey}">
                    <Say>{response}</Say>
                </GetDigits>
                """

    @staticmethod
    def partial_record(
        response, trim_silence=True, play_beep=True, finishOnKey="#", maxLength=10
    ):
        return f"""
                <Record finishOnKey="{finishOnKey}" maxLength="{maxLength}" trimSilence="{trim_silence}" playBeep="{play_beep}">
                    <Say>{response}</Say>
                </Record>
                """

    @staticmethod
    def terminal_record(response, play_beep=True):
        return f"""
                <Say playBeep="{play_beep}">{response}</Say>
                <Record />
                """