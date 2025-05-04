from uagents import Agent, Context, Model
from typing import Any, Dict
class UserRequest(Model):
    text: str

class UserResponse(Model):
    uid: str = None
    text: str = None
    link: str = None
    error: str = None

user_agent = Agent(name="UserAgent")

@user_agent.on_rest_post("/user/input", UserRequest, UserResponse)
async def handle_user_input(ctx: Context, req: UserRequest) -> UserResponse:
    ctx.logger.info(f"Received user input: {req.text}")

    # Step 1: Send to Combined Agent (Ethics + Text Generation)
    combined_response = await ctx.rest_post(
        "/process-text",  # Combined Agent endpoint
        {"text": req.text},
    )

    if "error" in combined_response:
        ctx.logger.error(f"Error from Combined Agent: {combined_response['error']}")
        return UserResponse(error=combined_response["error"])

    uid = combined_response["uid"]
    generated_text = combined_response["text"]

    # Step 2: Send to Voice Mode Agent
    ctx.logger.info(f"Forwarding generated text to Voice Mode Agent: {generated_text}")
    try:
        voice_response = await ctx.rest_post(
            "http://localhost:8003/generate-voice",  # Voice Mode Agent endpoint
            {"text": generated_text},
        )
        if "error" in voice_response:
            ctx.logger.error(f"Error from Voice Mode Agent: {voice_response['error']}")
            return UserResponse(uid=uid, text=generated_text, error=voice_response["error"])
        sound_link = voice_response["link"]
    except Exception as e:
        ctx.logger.error(f"Error while sending to Voice Mode Agent: {e}")
        return UserResponse(uid=uid, text=generated_text, error="500 Internal server error.")

    return UserResponse(uid=uid, text=generated_text, link=sound_link)

if __name__ == "__main__":
    user_agent.run()