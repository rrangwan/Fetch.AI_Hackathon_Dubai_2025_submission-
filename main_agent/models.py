from uagents import Model

class ASI1miniRequest(Model):
    query: str

class ASI1miniResponse(Model):
    response: str

class InfluencerTTSRequest(Model):
    text: str

class InfluencerTTSResponse(Model):
    uuid: str = None
    error: str = None
