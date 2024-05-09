import os
import random
from sarufi import Sarufi
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from mangum import Mangum


# Load environment variables
load_dotenv()

# Initialize Sarufi and get the bot
sarufi = Sarufi(api_key=os.getenv("SARUFI_API_KEY"))
sarufi_bot = sarufi.get_bot(os.getenv("SARUFI_BOT_ID"))

app = FastAPI()
handler = Mangum(app)


@app.post("/")
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
        sarufi_chat_id = f"{call_number}-{session_id}"
        if dtfm_digits:
            dtfm_digits = int(dtfm_digits.strip())

        if is_active == 1:
            # If the call is active, respond with a message and play an audio file
            sarufi_response = (
                sarufi_bot.respond("start", chat_id=sarufi_chat_id, channel="whatsapp")
                if not dtfm_digits
                else sarufi_bot.respond(dtfm_digits, chat_id=sarufi_chat_id, channel="whatsapp")
            )

            print(sarufi_response)
            next_state = sarufi_response.get("next_state")
            if sarufi_response.get("actions"):
                actions = sarufi_response.get("actions")
                for action in actions:
                    if action.get("send_audios"):
                        s_response = action.get("send_audios")
                        url_obj = random.choice(s_response)
                        if url_obj.get("link"):
                            s_response = url_obj.get("link")
                            if s_response:
                                if next_state != "end":
                                    response = VoiceResponse.get_digits(
                                        s_response, action="play"
                                    )
                                else:
                                    response = VoiceResponse.play(s_response)

                                template = (
                                    '<?xml version="1.0" encoding="UTF-8"?>'
                                    "<Response>"
                                    f"{response}"
                                    "</Response>"
                                )
                                response = template.format(response=response)
                                print(response)
                                return Response(
                                    content=response, media_type="application/xml"
                                )
                            print("No audio link found 1")
                        print("No audio link found 2")
                    if action.get("send_message"):
                        s_response = action.get("send_message")
                        s_response = ".".join(s_response)
                        if s_response and s_response != ".":
                            if next_state != "end":
                                response = VoiceResponse.get_digits(s_response)
                            else:
                                response = VoiceResponse.say(s_response)
                            template = (
                                '<?xml version="1.0" encoding="UTF-8"?>'
                                "<Response>"
                                f"{response}"
                                "</Response>"
                            )
                            response = template.format(response=response)
                            return Response(
                                content=response, media_type="application/xml"
                            )
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
        return f'<Play url="{response}" />'

    @staticmethod
    def get_digits(response, timeout=20, finishOnKey="#", action="say"):
        if action == "play":
            action = f'<Play url="{response}" />'
            return f"""
                <GetDigits timeout="{timeout}" finishOnKey="{finishOnKey}">
                    {action}
                </GetDigits>
                """
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
