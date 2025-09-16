from fastapi.responses import Response

class ExotelProvider:
    name = "EXOTEL"

    async def initiate_call(self, to_number: str, from_number: str | None = None) -> str:
        return f"EXO_mock_{abs(hash(to_number))%10_000}"

    def build_say(self, text: str, lang: str = "en") -> str:
        return f"<Say>{text}</Say>"

    def build_gather(self, prompt: str, num_digits: int = 1, input_mode: str = "dtmf", lang: str = "en") -> str:
        # Exotel XML semantics vary; keep a compatible stub
        return f"<Gather numDigits='{num_digits}'>{self.build_say(prompt, lang=lang)}</Gather>"

    def wrap_response(self, inner_xml: str) -> str:
        return f"<Response>{inner_xml}</Response>"

    def XMLResponse(self, xml: str):
        return Response(content=xml, media_type="application/xml")

    def verify_signature(self, raw_body: bytes, headers: dict) -> bool:
        return True
