from uagents import Context

class DatabaseConnection:
    def set_payment(self, ctx:Context, uid:str, text: str) -> None:
        ctx.storage.set(uid, text)

    def get_payment(self, ctx:Context, uid: str) -> str:
        return ctx.storage.get(uid)

    def remove_payment(self, ctx:Context, uid: str) -> None:
        ctx.storage.remove(uid)