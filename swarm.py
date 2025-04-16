
import subprocess
import time
import sys
import os
import autogen
import asyncio
from dotenv import load_dotenv
import logging
import requests

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OLLAMA_MODEL = "mistral"
OLLAMA_ARGS = "--n_ctx 8192 --flash-attn 1 --offload 1"
QUANTIZED_MODEL = "mistral:Q4_0"
AGENT_NAMES = ["Scout", "Editor", "Uploader", "Clicker", "Transaction", "Trader"]
REQUIRED_PACKAGES = ["autogen", "python-dotenv", "ag2[ollama]", "fix_busted_json"]

# Function to install dependencies
def install_dependencies():
    for package in REQUIRED_PACKAGES:
        while True:
            try:
                logger.info(f"🔧 Installing {package}...")
                subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", package], check=True)
                logger.info(f"✅ {package} installed successfully.")
                break
            except subprocess.CalledProcessError:
                logger.warning(f"⚠️ Failed to install {package}. Retrying in 5 seconds...")
                time.sleep(5)

def check_ollama_command():
    try:
        subprocess.run(["ollama", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def stop_ollama():
    subprocess.run(["ollama", "stop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def start_ollama():
    subprocess.run(["ollama", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def check_model_loaded():
    try:
        output = subprocess.check_output(["ollama", "list"], text=True, timeout=10)
        return OLLAMA_MODEL in output or QUANTIZED_MODEL in output
    except Exception:
        return False

def switch_to_quantized():
    global OLLAMA_MODEL, OLLAMA_ARGS
    logger.info("⚡ Switching to quantized model (Q4_0) for stability...")
    OLLAMA_MODEL = QUANTIZED_MODEL
    OLLAMA_ARGS = "--n_ctx 4096"

def create_agents():
    agents = []
    for name in AGENT_NAMES:
        try:
            agent = autogen.AssistantAgent(name=name, llm_config={"model": OLLAMA_MODEL, "api_type": "ollama"})
            agents.append(agent)
        except Exception as e:
            logger.error(f"💥 Error creating agent {name}: {e}")
    return agents

def collect_data_from_gate_io():
    api_key = os.getenv("GATE_IO_API_KEY")
    api_secret = os.getenv("GATE_IO_API_SECRET")
    if not api_key or not api_secret:
        logger.warning("⚠️ Gate.io API key or secret not set.")
        return None
    try:
        response = requests.get("https://api.gate.io/api2/1/ticker/btc_usdt")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"❌ Error collecting data: {e}")
        return None

def make_trade_on_gate_io():
    api_key = os.getenv("GATE_IO_API_KEY")
    api_secret = os.getenv("GATE_IO_API_SECRET")
    if not api_key or not api_secret:
        logger.warning("⚠️ Gate.io API key or secret not set.")
        return False
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
        response = requests.post("https://api.gate.io/api2/1/private/buy", json=payload, headers=headers)
        response.raise_for_status()
        logger.info("✅ Trade executed successfully.")
        return True
    except Exception as e:
        logger.error(f"❌ Trade failed: {e}")
        return False

def run_swarm():
    agents = create_agents()
    if not agents:
        logger.error("💥 No agents created. Exiting.")
        return
    groupchat = autogen.GroupChat(agents=agents, messages=[])
    controller = autogen.GroupChatManager(groupchat=groupchat)

    logger.info("🧠 Agents executing...")
    asyncio.run(asyncio.gather(*[a.run(f"Task for {a.name}") for a in agents]))

    data = collect_data_from_gate_io()
    if data:
        make_trade_on_gate_io()

def hyperloop():
    install_dependencies()

    if not check_ollama_command() or not os.getenv("OLLAMA_API_KEY"):
        logger.warning("⚠️ Skipping Ollama setup (missing command or API key).")
        run_swarm()
        return

    stop_ollama()

    for attempt in range(1000):
        logger.info(f"🔁 [Attempt {attempt + 1}] Booting Ollama...")

        start_ollama()
        time.sleep(5)

        if check_model_loaded():
            logger.info("✅ Ollama model loaded.")
            run_swarm()
            break
        else:
            logger.warning("❌ Model not loaded. Retrying...")
            stop_ollama()
            time.sleep(3)

        if attempt == 5:
            switch_to_quantized()

if __name__ == "__main__":
    hyperloop()
```

---

Let me know if you want this deployed or tailored to a specific system/agent logic (e.g. no Ollama agents at all).