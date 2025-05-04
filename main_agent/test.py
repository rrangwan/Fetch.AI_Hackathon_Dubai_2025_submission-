
import asyncio
import time
from uagents import Agent, Context, Protocol

from models import EthicsRequest, EthicsResponse, PaymentRequest, PaymentResponse

agent_address = input("Enter the address of the influencer agent: ")
text = input("Enter the message to send: ")

tester = Agent(name="Tester.AI", port=5000, seed="1234", endpoint="http://localhost:5000/submit")

influencer_protocol = Protocol(name="influencer_protocol", version="1.0")

@tester.on_event("startup")
async def send_message(ctx: Context):
    msg = EthicsRequest(text=text)
    asyncio.create_task(ctx.send(agent_address, msg))

@influencer_protocol.on_message(EthicsResponse)
async def handle_response(ctx: Context, sender: str, message: EthicsResponse):
    if message.error:
        ctx.logger.info(f"Error from influencer agent: {message.error}")
        return

    uid = message.uid    
    ctx.logger.info(f"Received response from influencer agent: {uid}")

    time.sleep(5)

    # Send payment request
    await ctx.send(agent_address, PaymentRequest(uid=uid))

@influencer_protocol.on_message(PaymentResponse)
async def handle_payment_response(ctx: Context, sender: str, message: PaymentResponse):
    if message.error:
        ctx.logger.info(f"Error from influencer agent: {message.error}")
        return

    link = message.link
    ctx.logger.info(f"Received payment link from influencer agent: {link}")
        
tester.include(influencer_protocol)

tester.run()