from app.telephony.provider_registry import get_provider

class DialerService:
    @staticmethod
    async def call(to_number: str, from_number: str | None = None) -> str:
        provider = get_provider()
        return await provider.initiate_call(to_number, from_number)
