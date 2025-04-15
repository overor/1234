import os
import requests
import logging

logger = logging.getLogger(__name__)

def collect_data_from_gate_io():
    logger.info("Collecting data from gate.io...")
    api_key = os.getenv("GATE_IO_API_KEY")
    api_secret = os.getenv("GATE_IO_API_SECRET")
    if not api_key or not api_secret:
        logger.error("❌ Gate.io API key or secret not set.")
        return None

    url = "https://api.gate.io/api2/1/ticker/btc_usdt"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        logger.info("✅ Data collected successfully from gate.io.")
        return data
    except requests.RequestException as e:
        logger.error(f"❌ Error collecting data from gate.io: {e}")
        return None

def make_trade_on_gate_io():
    logger.info("Making trade on gate.io...")
    api_key = os.getenv("GATE_IO_API_KEY")
    api_secret = os.getenv("GATE_IO_API_SECRET")
    if not api_key or not api_secret:
        logger.error("❌ Gate.io API key or secret not set.")
        return False

    url = "https://api.gate.io/api2/1/private/buy"
    payload = {
        "currencyPair": "btc_usdt",
        "rate": "50000",
        "amount": "0.01"
    }
    headers = {
        "Content-Type": "application/json",
        "KEY": api_key,
        "SIGN": api_secret
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logger.info("✅ Trade executed successfully on gate.io.")
        return True
    except requests.RequestException as e:
        logger.error(f"❌ Error making trade on gate.io: {e}")
        return False
