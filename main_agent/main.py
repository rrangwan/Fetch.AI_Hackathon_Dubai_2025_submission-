import uuid
from database import DatabaseConnection
from main_agent.waver import waver_generate_sound
from request_fabric import make_celebrity_request, make_ethical_request
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from env import SEED
from models import InfluencerPaymentRequest, InfluencerPaymentResponse, InfluencerTTSRequest, InfluencerTTSResponse
from asi1 import asi1_send_request

database = DatabaseConnection()
agent = Agent(name="Influencer.AI", seed=SEED, endpoint="http://localhost:8000/submit")
fund_agent_if_low(agent.wallet.address())

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("Shutting down the agent.")
    

@agent.on_message(InfluencerTTSRequest)
async def check_ethics(ctx: Context, sender: str, message: InfluencerTTSRequest):
    ctx.logger.info(f"Forwarding to ASI:ONE: {message.text}")

    if len(message.text) == 0 or len(message.text) > 1000:
        ctx.logger.info(f"Message is too long or empty: {message.text}")
        await ctx.send(sender, InfluencerTTSResponse(error="400 Invalid arguments."))
        return

    text = message.text
    context, response_schema = make_ethical_request()

    result = ""
    try:
        result = asi1_send_request(context=context, prompt=text, response_schema=response_schema)
    except Exception as e:
        ctx.logger.error(f"Error while sending request to ASI1: {e}")
        await ctx.send(sender, InfluencerTTSResponse(error="500 Internal server error."))
        return

    ctx.logger.info(f"ASI1 Result: {result}")
    if result != "y":
        ctx.logger.info(f"Message is unethical: {text}")
        response = InfluencerTTSResponse(error="400 Invalid arguments.")
        await ctx.send(sender, response)
        return
    ctx.logger.info(f"Message is ethical: {text}")

    uid = str(uuid.uuid4())

    try:
        database.set_payment(ctx, uid, text)
    except Exception as e:
        ctx.logger.error(f"Error while adding payment holder to database: {e}")
        await ctx.send(sender, InfluencerTTSResponse(error="500 Internal server error."))
        return

    await ctx.send(sender, InfluencerTTSResponse(uid=uid))

@agent.on_message(InfluencerPaymentRequest)
async def check_payment(ctx: Context, sender: str, message: InfluencerPaymentRequest):
    ctx.logger.info(f"Checking payment for UID: {message.uid}")
    text = None
    try:
        text = database.get_payment(ctx, message.uid)
    except Exception as e:
        ctx.logger.error(f"Error while getting payment from database: {e}")
        await ctx.send(sender, InfluencerPaymentResponse(error="500 Internal server error."))
        return

    if text is None:
        ctx.logger.info(f"Payment not found for UID: {message.uid}")
        await ctx.send(sender, InfluencerPaymentResponse(error="400 Invalid arguments."))
        return

    context, response_schema = make_celebrity_request()
    generatedText = ""
    uid = message.uid

    try:
        generatedText = asi1_send_request(context=context, prompt=text, response_schema=response_schema)
    except Exception as e:
        ctx.logger.error(f"Error while sending request to ASI1: {e}")
        await ctx.send(sender, InfluencerPaymentResponse(error="500 Internal server error."))
        return

    DatabaseConnection.remove_payment(ctx, uid)

    sound_link = None
    try:
        sound_link = waver_generate_sound(generatedText)
    except Exception as e:
        ctx.logger.error(f"Error while sending generate sound request: {e}")
        await ctx.send(sender, InfluencerPaymentResponse(error="500 Internal server error."))
        return

    await ctx.send(sender, InfluencerPaymentResponse(link=sound_link))

if __name__ == "__main__":
    agent.run()