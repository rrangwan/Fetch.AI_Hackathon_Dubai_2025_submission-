from uagents import Agent, Context, Model
from main_agent.waver import waver_generate_sound
import requests

class VoiceRequest(Model):
    text: str

class VoiceResponse(Model):
    link: str = None
    error: str = None

voice_agent = Agent(name="VoiceModeAgent")

@voice_agent.on_message(VoiceRequest)
async def process_text_and_generate_voice(ctx: Context, sender: str, req: VoiceRequest):
    ctx.logger.info(f"Received text for processing: {req.text}")

    # Step 1: Post the text to the external model
    external_model_url = "http://external-model.com/process"  # Replace with the actual URL
    model_payload = {"text": req.text}
    try:
        model_response = requests.post(external_model_url, json=model_payload)
        model_response.raise_for_status()  # Raise an exception for HTTP errors
        processed_text = model_response.json().get("result")
        if not processed_text:
            raise ValueError("Model response does not contain 'result'")
        ctx.logger.info(f"Successfully processed text: {processed_text}")
    except requests.exceptions.RequestException as e:
        ctx.logger.error(f"Error posting to external model: {e}")
        await ctx.send(sender, VoiceResponse(error="500 Error posting to external model."))
        return
    except ValueError as e:
        ctx.logger.error(f"Invalid response from model: {e}")
        await ctx.send(sender, VoiceResponse(error="500 Invalid response from model."))
        return

    # Step 2: Generate the voice file
    try:
        sound_link = waver_generate_sound(processed_text)
        ctx.logger.info(f"Generated voice file link: {sound_link}")
    except Exception as e:
        ctx.logger.error(f"Error during voice generation: {e}")
        await ctx.send(sender, VoiceResponse(error="500 Internal server error during voice generation."))
        return

    # Step 3: Respond back to the sender with the download link
    await ctx.send(sender, VoiceResponse(link=sound_link))

if __name__ == "__main__":
    voice_agent.run()