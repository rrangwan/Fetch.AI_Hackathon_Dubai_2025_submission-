from uagents import Model

class ASI1miniRequest(Model):
    query: str

class ASI1miniResponse(Model):
    response: str

class InfluencerTTSRequest(Model):
    text: str

class InfluencerTTSResponse(Model):
    uid: str = None
    error: str = None

class InfluencerPaymentRequest(Model):
    uid: str

class InfluencerPaymentResponse(Model):
    link: str = None
    error: str = None
    