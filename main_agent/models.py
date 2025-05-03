from uagents import Model

class ASI1miniRequest(Model):
    query: str

class ASI1miniResponse(Model):
    response: str

class InfluencerRequest(Model):
    text: str

class InfluencerResponse(Model):
    status: str
    error: str = None
