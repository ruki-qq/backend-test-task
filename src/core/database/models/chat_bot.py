from beanie import Document


class ChatBot(Document):
    name: str
    secret_token: str
