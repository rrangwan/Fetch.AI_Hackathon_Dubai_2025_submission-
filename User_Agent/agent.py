"""
Bob Agent - Receives payments via TransactAI
"""

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

# Bob agent setup
bob = Agent()

@bob.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Bob started. Address: {bob.address}")
    ctx.logger.info(f"Wallet address: {bob.wallet.address()}")

    # Give agents time to register etc.
    await asyncio.sleep(5.0)

    # 1. Register Agent with TransactAI
    ctx.logger.info("Registering agent with TransactAI...")
    register_msg = create_metadata_message({'command': 'register'})
    await ctx.send(TRANSACTAI_ADDRESS, register_msg)
    await asyncio.sleep(2.0) # Wait briefly

    # 2. Register Wallet with TransactAI
    ctx.logger.info("Registering wallet with TransactAI...")
    wallet_address = str(bob.wallet.address()) # Get Bob's wallet address
    register_wallet_msg = create_metadata_message({
        'command': 'register_wallet',
        'wallet_address': wallet_address
    })
    await ctx.send(TRANSACTAI_ADDRESS, register_wallet_msg)
    await asyncio.sleep(2.0) # Wait briefly

# Handle responses/notifications from TransactAI
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
                             'wallet_address': str(bob.wallet.address()), # Bob's own wallet
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

# Include the protocol
bob.include(agent_proto)

if __name__ == "__main__":
    print(f"Bob starting. Address: {bob.address}")
    bob.run()