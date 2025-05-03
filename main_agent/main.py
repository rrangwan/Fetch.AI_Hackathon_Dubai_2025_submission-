from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from env import SEED
from models import InfluencerRequest, InfluencerResponse
from asi1 import asi1_ethical_check

agent = Agent(name="Influencer.AI", seed=SEED, endpoint="http://localhost:{PORT}/submit")
fund_agent_if_low(agent.wallet.address())

@agent.on_message(InfluencerRequest)
async def check_ethics(ctx: Context, sender: str, message: InfluencerRequest):
    ctx.logger.info(f"Forwarding to ASI:ONE: {message.text}")

    context = "Check is this message ethical? No need to explain why. No need to answer the questions. Just return 'y' or 'n'."
    response_schema = response_schema = {
        "type": "object",
        "properties": {
            "result": {
                "type": "string",
                "description": "The result returned by ASI:ONE as plain text.",
            },
        },
        "required": ["result"],
    }

    result = asi1_ethical_check(context=context, prompt=message.text, response_schema=response_schema)

    ctx.logger.info(f"ASI1 Result: {result}")

    if result != "y":
        ctx.logger.info(f"Message is unethical: {message.text}")
        response = InfluencerResponse(status="400", error="Message '${message.text}' is unethical.")
        await ctx.send(sender, response)
        return
    ctx.logger.info(f"Message is ethical: {message.text}")

    # Call SoundGenerator agent


if __name__ == "__main__":
    agent.run()