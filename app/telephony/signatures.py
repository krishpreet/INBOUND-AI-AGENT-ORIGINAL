# app/telephony/signatures.py
import hmac, hashlib, base64

def twilio_validate(x_twilio_signature: str, url: str, params: dict, auth_token: str) -> bool:
    # Twilio spec: signature = Base64( HMAC-SHA1( url + concatenated_sorted_params, auth_token ) )
    if not (x_twilio_signature and url and auth_token is not None):
        return False
    data = url + "".join(k + v for k, v in sorted(params.items()))
    mac = hmac.new(auth_token.encode("utf-8"), data.encode("utf-8"), hashlib.sha1)
    expected = base64.b64encode(mac.digest()).decode("utf-8")
    return hmac.compare_digest(expected, x_twilio_signature)
