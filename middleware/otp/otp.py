import pyotp
from logger import logger

def generate_otp(secret:str) -> str:
    totp = pyotp.TOTP(secret)
    logger.info(f"Generated OTP: {totp.now()}")
    return totp.now()

def verify_otp(otp: str,secret:str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(otp)