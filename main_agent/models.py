from uagents import Model

class EthicsRequest(Model):
    text: str

class EthicsResponse(Model):
    uid: str = None
    error: str = None

class PaymentRequest(Model):
    uid: str

class PaymentResponse(Model):
    link: str = None
    error: str = None