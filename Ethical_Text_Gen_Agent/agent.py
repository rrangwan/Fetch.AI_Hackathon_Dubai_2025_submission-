from uagents import Agent, Context, Model
from asi1 import asi1_send_request
from request_fabric import make_ethical_request, make_celebrity_request
from typing import Dict, Any
import uuid

class CombinedRequest(Model):
    text: str

class CombinedResponse(Model):
    uid: str = None
    text: str = None
    error: str = None

combined_agent = Agent(name="EthicsAndTextGenAgent")

@combined_agent.on_rest_post("/process-text", CombinedRequest, CombinedResponse)
async def process_text(ctx: Context, req: CombinedRequest) -> CombinedResponse:
    ctx.logger.info(f"Processing text: {req.text}")

    # Step 1: Perform Ethics Check
    context, response_schema = make_ethical_request()
    try:
        ethics_result = asi1_send_request(context=context, prompt=req.text, response_schema=response_schema)
    except Exception as e:
        ctx.logger.error(f"Error during ethics check: {e}")
        return CombinedResponse(error="500 Internal server error during ethics check.")

    if ethics_result != "y":
        ctx.logger.info(f"Text failed ethics check: {req.text}")
        return CombinedResponse(error="400 Text is unethical.")

    # Step 2: Generate Celebrity-Style Text
    context, response_schema = make_celebrity_request()
    try:
        generated_text = asi1_send_request(context=context, prompt=req.text, response_schema=response_schema)
    except Exception as e:
        ctx.logger.error(f"Error during text generation: {e}")
        return CombinedResponse(error="500 Internal server error during text generation.")

    # Generate a unique UID for tracking
    uid = str(uuid.uuid4())

    return CombinedResponse(uid=uid, text=generated_text)

if __name__ == "__main__":
    combined_agent.run()