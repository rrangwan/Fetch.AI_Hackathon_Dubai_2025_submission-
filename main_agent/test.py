
from uagents import Agent, Context

from models import InfluencerTTSRequest, InfluencerTTSResponse

agent_address = input("Enter the address of the influencer agent: ")
text = input("Enter the message to send: ")

tester = Agent(name="Tester.AI", port=5000, seed="1234", endpoint="http://localhost:5000/submit")

@tester.on_event("startup")
async def send_message(ctx: Context):
    msg = InfluencerTTSRequest(text=text)
    _, status = await ctx.send_and_receive(agent_address, msg, response_type=InfluencerTTSResponse)
    ctx.logger.info(f"Tester request status: {status}")

tester.run()