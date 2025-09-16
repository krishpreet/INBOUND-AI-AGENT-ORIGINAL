def say(text: str, lang: str = "en") -> str:
    return f"<Say language='{lang}'>{text}</Say>"

def gather(prompt: str, num_digits: int = 1) -> str:
    return f"<Gather numDigits='{num_digits}'>{say(prompt)}</Gather>"

def wrap(inner: str) -> str:
    return f"<Response>{inner}</Response>"
