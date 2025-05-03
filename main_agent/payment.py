import uuid

class Payment:
    uid: str
    text: str

    def __init__(self, text: str):
        self.text = text
        self.uid = str(uuid.uuid4())