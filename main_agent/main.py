from database import DatabaseConnection
from payment import Payment
from request_fabric import make_celebrity_request, make_ethical_request
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from env import SEED
from models import InfluencerPaymentRequest, InfluencerPaymentResponse, InfluencerTTSRequest, InfluencerTTSResponse
from asi1 import asi1_send_request

database = DatabaseConnection("./database.db")
agent = Agent(name="Influencer.AI", seed=SEED, endpoint="http://localhost:8000/submit")
fund_agent_if_low(agent.wallet.address())

@agent.on_event("startup")
async def startup(ctx: Context):
    database.setup()

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    database.close()

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

    payment = Payment(text)
    
    try:
        database.add_payment_holder(payment)
    except Exception as e:
        ctx.logger.error(f"Error while adding payment holder to database: {e}")
        await ctx.send(sender, InfluencerTTSResponse(error="500 Internal server error."))
        return

    await ctx.send(sender, InfluencerTTSResponse(uid=payment.uid))

@agent.on_message(InfluencerPaymentRequest)
async def check_payment(ctx: Context, sender: str, message: InfluencerPaymentRequest):
    ctx.logger.info(f"Checking payment for UID: {message.uid}")
    text = ""
    try:
        text = database.mark_payment_as_payed(message.uid)
    except Exception as e:
        ctx.logger.error(f"Error while getting payment from database: {e}")
        await ctx.send(sender, InfluencerPaymentResponse(error="500 Internal server error."))
        return

    context, response_schema = make_celebrity_request()
    result = ""
    try:
        result = asi1_send_request(context=context, prompt=text, response_schema=response_schema)
    except Exception as e:
        ctx.logger.error(f"Error while sending request to ASI1: {e}")
        await ctx.send(sender, InfluencerPaymentResponse(error="500 Internal server error."))
        return
    ctx.logger.info(f"Celebrity talks: {result}")
    await ctx.send(sender, InfluencerPaymentResponse(link=result))
    

if __name__ == "__main__":
    agent.run()