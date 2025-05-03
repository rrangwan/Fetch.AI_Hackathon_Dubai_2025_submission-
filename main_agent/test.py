
import time
from uagents import Agent, Context

from models import InfluencerPaymentRequest, InfluencerPaymentResponse, InfluencerTTSRequest, InfluencerTTSResponse

agent_address = input("Enter the address of the influencer agent: ")
text = input("Enter the message to send: ")

tester = Agent(name="Tester.AI", port=5000, seed="1234", endpoint="http://localhost:5000/submit")

@tester.on_event("startup")
async def send_message(ctx: Context):
    msg = InfluencerTTSRequest(text=text)
    await ctx.send(agent_address, msg)

@tester.on_message(InfluencerTTSResponse)
async def handle_response(ctx: Context, sender: str, message: InfluencerTTSResponse):
    if message.error:
        ctx.logger.info(f"Error from influencer agent: {message.error}")
        return

    uid = message.uid    
    ctx.logger.info(f"Received response from influencer agent: {uid}")

    time.sleep(5)

    # Send payment request
    await ctx.send(agent_address, InfluencerPaymentRequest(uid=uid))

@tester.on_message(InfluencerPaymentResponse)
async def handle_payment_response(ctx: Context, sender: str, message: InfluencerPaymentResponse):
    if message.error:
        ctx.logger.info(f"Error from influencer agent: {message.error}")
        return

    link = message.link
    ctx.logger.info(f"Received payment link from influencer agent: {link}")
        

tester.run()