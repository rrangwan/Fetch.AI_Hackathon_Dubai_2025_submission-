import uuid
from database import DatabaseConnection
from models import EthicsRequest, EthicsResponse, PaymentRequest, PaymentResponse
from waver import waver_generate_sound
from request_fabric import make_celebrity_request, make_ethical_request
from uagents import Agent, Context, Protocol, Model
from uagents.setup import fund_agent_if_low
from env import SEED
from asi1 import asi1_send_request
import asyncio
from uagents import Agent, Context
from datetime import datetime

# Import the custom agent protocol
from agent_protocol import (
    agent_proto,
    AgentMessage,
    AgentAcknowledgement,
    create_metadata_message
)

# TransactAI agent address (ensure this is correct)
TRANSACTAI_ADDRESS = "agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq"

# Initialize the database and agent
database = DatabaseConnection()
agent = Agent(name="Influencer.AI", seed=SEED)
fund_agent_if_low(agent.wallet.address())

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Agent started. Address: {agent.address}")
    ctx.logger.info(f"Wallet address: {agent.wallet.address()}")

    # Give agents time to register etc.
    await asyncio.sleep(5.0)

    # 1. Register Agent with TransactAI
    ctx.logger.info("Registering agent with TransactAI...")
    register_msg = create_metadata_message({'command': 'register'})
    await ctx.send(TRANSACTAI_ADDRESS, register_msg)
    await asyncio.sleep(2.0)  # Wait briefly

    # 2. Register Wallet with TransactAI
    ctx.logger.info("Registering wallet with TransactAI...")
    wallet_address = str(agent.wallet.address())  # Get agent's wallet address
    register_wallet_msg = create_metadata_message({
        'command': 'register_wallet',
        'wallet_address': wallet_address
    })
    await ctx.send(TRANSACTAI_ADDRESS, register_wallet_msg)
    await asyncio.sleep(2.0)  # Wait briefly

@agent_proto.on_message(model=AgentMessage)
async def handle_transactai_message(ctx: Context, sender: str, msg: AgentMessage):
    ctx.logger.info(f"Received message from {sender}")
    for content in msg.content:
        if content.type == "metadata":
            metadata = content.metadata
            ctx.logger.info(f"Metadata: {metadata}")
            
            command = metadata.get('command')
            status = metadata.get('status')

            if command == 'register_response':
                ctx.logger.info(f"Registration response: {status}")
            elif command == 'payment_received':
                ctx.logger.info(f"Payment received from {metadata.get('from')}!")
                amount_received_str = metadata.get('amount')
                ctx.logger.info(f"Amount: {amount_received_str}, Reference: {metadata.get('reference')}")
                ctx.logger.info(f"New balance: {metadata.get('balance')}")

                # Attempt to withdraw the received amount
                try:
                    amount_to_withdraw = int(amount_received_str)
                    if amount_to_withdraw > 0:
                        ctx.logger.info(f"Attempting to withdraw received amount: {amount_to_withdraw}")
                        withdraw_msg = create_metadata_message({
                            'command': 'withdraw',
                            'amount': str(amount_to_withdraw),
                            'wallet_address': str(agent.wallet.address()),  # agent's own wallet
                            'denom': "atestfet"
                        })
                        # Send withdrawal request asynchronously
                        asyncio.create_task(ctx.send(TRANSACTAI_ADDRESS, withdraw_msg))
                    else:
                        ctx.logger.info("Received payment amount is zero or invalid, not withdrawing.")
                except (ValueError, TypeError) as e:
                    ctx.logger.error(f"Could not parse amount for withdrawal: {amount_received_str}, Error: {e}")

            elif command == 'withdraw_confirmation':
                ctx.logger.info(f"Withdrawal confirmation received: {metadata}")
                if status == 'success':
                    ctx.logger.info(f"Withdrawal successful! Tx: {metadata.get('tx_hash')}, New balance: {metadata.get('balance')}")
                else:
                    ctx.logger.error(f"Withdrawal failed! Reason: {metadata.get('reason')}")

            # Handle other relevant messages like escrow notifications if needed
        
        elif content.type == "text":
            ctx.logger.info(f"Text: {content.text}")

    # Send acknowledgement back to TransactAI
    await ctx.send(sender, AgentAcknowledgement(
        timestamp=datetime.utcnow(),
        acknowledged_msg_id=msg.msg_id
    ))

# Handle acknowledgements (optional)
@agent_proto.on_message(model=AgentAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: AgentAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}")

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
agent.include(agent_proto)

if __name__ == "__main__":
    agent.run()