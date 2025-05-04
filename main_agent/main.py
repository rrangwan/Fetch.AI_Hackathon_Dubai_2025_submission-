import uuid
from database import DatabaseConnection
from models import EthicsRequest, EthicsResponse, PaymentRequest, PaymentResponse
from waver import waver_generate_sound
from request_fabric import make_celebrity_request, make_ethical_request
from uagents import Agent, Context, Protocol, Model
from uagents.setup import fund_agent_if_low
from env import SEED
from asi1 import asi1_send_request

# Initialize the database and agent
database = DatabaseConnection()
agent = Agent(name="Influencer.AI", seed=SEED, endpoint="http://localhost:8000/submit")
fund_agent_if_low(agent.wallet.address())

# Define the protocol
influencer_protocol = Protocol(name="influencer_protocol", version="1.0")

# Step 1: Handle Ethical Check
@influencer_protocol.on_message(model=EthicsRequest, replies=EthicsResponse)
async def handle_ethics_check(ctx: Context, sender: str, req: EthicsRequest):
    ctx.logger.info(f"Received text for ethical check: {req.text}")

    if len(req.text) == 0 or len(req.text) > 1000:
        ctx.logger.info(f"Message is too long or empty: {req.text}")
        await ctx.send(sender, EthicsResponse(error="400 Invalid arguments."))
        return

    context, response_schema = make_ethical_request()
    try:
        result = asi1_send_request(context=context, prompt=req.text, response_schema=response_schema)
    except Exception as e:
        ctx.logger.error(f"Error during ethics check: {e}")
        await ctx.send(sender, EthicsResponse(error="500 Internal server error."))
        return

    if result != "y":
        ctx.logger.info(f"Message is unethical: {req.text}")
        await ctx.send(sender, EthicsResponse(error="400 Text is unethical."))
        return

    uid = str(uuid.uuid4())
    try:
        database.set_payment(ctx, uid, req.text)
    except Exception as e:
        ctx.logger.error(f"Error while storing payment information: {e}")
        await ctx.send(sender, EthicsResponse(error="500 Internal server error."))
        return

    await ctx.send(sender, EthicsResponse(uid=uid))

# Step 2: Handle Payment and Text Generation
@influencer_protocol.on_message(model=PaymentRequest, replies=PaymentResponse)
async def handle_payment_and_text_generation(ctx: Context, sender: str, req: PaymentRequest):
    ctx.logger.info(f"Processing payment for UID: {req.uid}")

    try:
        text = database.get_payment(ctx, req.uid)
    except Exception as e:
        ctx.logger.error(f"Error while retrieving payment information: {e}")
        await ctx.send(sender, PaymentResponse(error="500 Internal server error."))
        return

    if text is None:
        ctx.logger.info(f"No payment found for UID: {req.uid}")
        await ctx.send(sender, PaymentResponse(error="400 Invalid arguments."))
        return

    context, response_schema = make_celebrity_request()
    generated_text = None
    try:
        generated_text = asi1_send_request(context=context, prompt=text, response_schema=response_schema)
    except Exception as e:
        ctx.logger.error(f"Error during text generation: {e}")
        await ctx.send(sender, PaymentResponse(error="500 Internal server error."))
        return

    try:
        database.remove_payment(ctx, req.uid)
    except Exception as e:
        ctx.logger.error(f"Error while removing payment information: {e}")
        await ctx.send(sender, PaymentResponse(error="500 Internal server error."))
        return

    try:
        sound_link = waver_generate_sound(generated_text)
    except Exception as e:
        ctx.logger.error(f"Error during voice generation: {e}")
        await ctx.send(sender, PaymentResponse(error="500 Internal server error."))
        return

    await ctx.send(sender, PaymentResponse(link=sound_link))

# Include the protocol in the agent
agent.include(influencer_protocol)

agent.run()