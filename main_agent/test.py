
import asyncio
import time
from uagents import Agent, Context, Protocol
from env import CELEBRITY_AI_ADDR, TEXT
from models import EthicsRequest, EthicsResponse, PaymentRequest, PaymentResponse

import asyncio
from uagents import Agent, Context
from uagents.network import get_ledger
from datetime import datetime

# Import the custom agent protocol
# Ensure agent_protocol.py is in the same directory or accessible in PYTHONPATH
try:
    from agent_protocol import (
        agent_proto,
        AgentMessage,
        AgentAcknowledgement,
        create_metadata_message
    )
except ImportError:
    print("Error: agent_protocol.py not found. Please ensure it's in the correct path.")
    # Define minimal models if import fails, to allow basic understanding
    from uagents import Model, Protocol
    from typing import List, Dict, Union, Literal, Optional
    from pydantic.v1 import Field, UUID4
    import uuid

    class MetadataContent(Model):
        type: Literal["metadata"] = "metadata"
        metadata: dict[str, str]
    AgentContent = Union[MetadataContent]
    class AgentMessage(Model):
        timestamp: datetime = Field(default_factory=datetime.utcnow)
        msg_id: UUID4 = Field(default_factory=uuid.uuid4)
        content: list[AgentContent]
    class AgentAcknowledgement(Model):
        timestamp: datetime = Field(default_factory=datetime.utcnow)
        acknowledged_msg_id: UUID4
        metadata: Optional[dict[str, str]] = None
    def create_metadata_message(metadata: Dict[str, str]) -> AgentMessage:
        return AgentMessage(content=[MetadataContent(metadata=metadata)])
    # Define a dummy protocol if needed for basic structure
    agent_proto = Protocol("DummyAgentProto", version="1.0")


# TransactAI agent address (ensure this is correct)
TRANSACTAI_ADDRESS = "agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq"
TRANSACTAI_WALLET = "fetch1uyxsdlejg7axp4dzmqpq54g0uwde5nv6fflhkv" # TransactAI's on-chain wallet

# Bob's agent address
BOB_ADDRESS = "agent1qwcjyh288szzhny06d6th3j6qkauxeljp94ps5vhkxl8ej6dclg9kvq6lss"

DEPOSIT_CONFIRMED_FLAG = "deposit_confirmed"
PAYMENT_ATTEMPTED_FLAG = "payment_attempted"




tester = Agent(name="Tester.AI", seed="1234")




influencer_protocol = Protocol(name="influencer_protocol", version="1.0")

@tester.on_event("startup")
async def startup(ctx: Context):

    ctx.logger.info(f"tester started. Address: {tester.address}")
    ctx.logger.info(f"Wallet address: {tester.wallet.address()}")

    # Initialize flags
    ctx.storage.set(DEPOSIT_CONFIRMED_FLAG, False)
    ctx.storage.set(PAYMENT_ATTEMPTED_FLAG, False)

    # 1. Register Agent with TransactAI
    ctx.logger.info("Registering agent with TransactAI...")
    register_msg = create_metadata_message({'command': 'register'})
    await ctx.send(TRANSACTAI_ADDRESS, register_msg)
    await asyncio.sleep(2.0) # Wait for agent registration

    # 2. Register Wallet with TransactAI
    ctx.logger.info("Registering wallet with TransactAI...")
    wallet_address = str(tester.wallet.address()) # Get tester's wallet address
    register_wallet_msg = create_metadata_message({
        'command': 'register_wallet',
        'wallet_address': wallet_address
    })
    await ctx.send(TRANSACTAI_ADDRESS, register_wallet_msg)
    await asyncio.sleep(5.0) # Wait for wallet registration

    # 3. On-chain deposit to TransactAI wallet
    ctx.logger.info("Sending on-chain deposit to TransactAI wallet...")
    deposit_amount = 1 # 0.1 testfet (needs enough for payment)
    tx_hash = None
    try:
        ledger = get_ledger("dorado") # Get ledger instance right before use
        # Ensure wallet has funds from faucet: https://companion.fetch.ai/dorado-1/accounts
        ctx.logger.info(f"Attempting to send {deposit_amount} atestfet to {TRANSACTAI_WALLET}")
        tx = ledger.send_tokens(TRANSACTAI_WALLET, deposit_amount, "atestfet", tester.wallet)
        result = tx.wait_to_complete()
        tx_hash = result.tx_hash
        ctx.logger.info(f"Deposit transaction hash: {tx_hash}")
    except Exception as e:
        ctx.logger.error(f"Error sending on-chain deposit: {e}")
        ctx.logger.error("Ensure tester's wallet has sufficient 'atestfet' from the faucet.")
        return

    # 4. Send deposit confirmation command to TransactAI
    if tx_hash:
        ctx.logger.info(f"Sending deposit confirmation command for tx_hash: {tx_hash}")
        deposit_confirm_msg = create_metadata_message({
            'command': 'deposit',
            'tx_hash': tx_hash,
            'amount': str(deposit_amount),
            'denom': "atestfet"
        })
        await ctx.send(TRANSACTAI_ADDRESS, deposit_confirm_msg)

        # Wait for deposit confirmation state change
        MAX_WAIT_TIME = 60 # seconds
        WAIT_INTERVAL = 5 # seconds
        time_waited = 0
        deposit_confirmed = False
        while time_waited < MAX_WAIT_TIME:
            if ctx.storage.get(DEPOSIT_CONFIRMED_FLAG) is True:
                deposit_confirmed = True
                ctx.logger.info("Deposit confirmed by TransactAI.")
                break
            ctx.logger.info(f"Waiting for deposit confirmation... ({time_waited}/{MAX_WAIT_TIME}s)")
            await asyncio.sleep(WAIT_INTERVAL)
            time_waited += WAIT_INTERVAL

        if not deposit_confirmed:
            ctx.logger.error("Timed out waiting for deposit confirmation from TransactAI.")
            return # Stop if deposit not confirmed

    else:
        ctx.logger.error("On-chain deposit failed, cannot proceed.")
        return # Stop if deposit failed

    # 5. Send payment to Bob via TransactAI (only if deposit confirmed and payment not already attempted)
    # This part is triggered by handle_transactai_response upon successful deposit confirmation
    # We call maybe_send_payment here just in case the confirmation message arrived *during* the wait loop
    await maybe_send_payment(ctx)
    msg = EthicsRequest(text=TEXT)
    asyncio.create_task(ctx.send(CELEBRITY_AI_ADDR, msg))


@agent_proto.on_message(model=AgentMessage)
async def handle_transactai_response(ctx: Context, sender: str, msg: AgentMessage):
    ctx.logger.info(f"Received message from {sender}")
    response_handled = False # Flag to ensure ack is sent even if no specific handler matches
    for content in msg.content:
        if content.type == "metadata":
            metadata = content.metadata
            ctx.logger.info(f"Metadata: {metadata}")
            
            command = metadata.get('command')
            status = metadata.get('status')

            if command == 'register_response':
                 ctx.logger.info(f"Registration response: {status}")
                 response_handled = True
            elif command == 'register_wallet_response':
                 ctx.logger.info(f"Wallet registration response: {status}")
                 response_handled = True
            elif command == 'deposit_response':
                 ctx.logger.info(f"Deposit response received: {metadata}")
                 if status == 'success':
                     ctx.storage.set(DEPOSIT_CONFIRMED_FLAG, True)
                     # If payment hasn't been attempted yet, trigger it now
                     asyncio.create_task(maybe_send_payment(ctx))
                 elif status == 'pending_confirmation':
                     ctx.logger.info("Deposit is still pending confirmation.")
                 else: # Failed
                     ctx.logger.error(f"Deposit failed: {metadata.get('reason')}")
                     # Consider setting a 'deposit_failed' flag if needed
                 response_handled = True
            elif command == 'payment_confirmation':
                 if status == 'success':
                     ctx.logger.info(f"Payment successful! New balance: {metadata.get('balance')}")
                 else:
                     ctx.logger.error(f"Payment failed! Reason: {metadata.get('reason')}, Balance: {metadata.get('balance')}")
                 response_handled = True
            # Handle other responses if needed (e.g., balance_response)
        
        elif content.type == "text":
            ctx.logger.info(f"Text: {content.text}")
            response_handled = True # Acknowledge text messages too

    # Send acknowledgement back to TransactAI if message was processed
    if response_handled:
        await ctx.send(sender, AgentAcknowledgement(
            timestamp=datetime.utcnow(),
            acknowledged_msg_id=msg.msg_id
        ))
    else:
        ctx.logger.warning(f"Received unhandled message content types from {sender}: {[c.type for c in msg.content]}")


# Separate function to attempt payment after deposit confirmation
async def maybe_send_payment(ctx: Context):
    # Ensure deposit is confirmed and payment hasn't been attempted
    if ctx.storage.get(DEPOSIT_CONFIRMED_FLAG) is True and not ctx.storage.get(PAYMENT_ATTEMPTED_FLAG):
        payment_amount = 1 # Example amount (0.1 atestfet)
        ctx.logger.info(f"Deposit confirmed, now attempting to pay {payment_amount} to Bob ({BOB_ADDRESS})...")
        ctx.storage.set(PAYMENT_ATTEMPTED_FLAG, True) # Mark as attempted
        payment_msg = create_metadata_message({
            'command': 'payment',
            'recipient': BOB_ADDRESS,
            'amount': str(payment_amount),
            'reference': f"payment-{datetime.utcnow().isoformat()}"
        })
        await ctx.send(TRANSACTAI_ADDRESS, payment_msg)

@agent_proto.on_message(model=AgentAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: AgentAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}")




@influencer_protocol.on_message(EthicsResponse)
async def handle_response(ctx: Context, sender: str, message: EthicsResponse):
    if message.error:
        ctx.logger.info(f"Error from influencer agent: {message.error}")
        return

    uid = message.uid    
    ctx.logger.info(f"Received response from influencer agent: {uid}")

    time.sleep(5)

    # Send payment request
    await ctx.send(CELEBRITY_AI_ADDR, PaymentRequest(uid=uid))

@influencer_protocol.on_message(PaymentResponse)
async def handle_payment_response(ctx: Context, sender: str, message: PaymentResponse):
    if message.error:
        ctx.logger.info(f"Error from influencer agent: {message.error}")
        return

    link = message.link
    ctx.logger.info(f"Received payment link from influencer agent: {link}")
        
tester.include(influencer_protocol)
tester.include(agent_proto)

if __name__ == "__main__":
    print(f"tester starting. Address: {tester.address}")
    print("Ensure agent_protocol.py is accessible.")
    print("CRITICAL: Replace the example tester_SEED in the code if using for anything beyond this demo.")
    tester.run()