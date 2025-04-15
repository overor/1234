#!/usr/bin/env python3
import subprocess
import time
import sys
import os
import autogen
import asyncio
from dotenv import load_dotenv
import logging
import random
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

# Function to check if ollama command is available
def check_ollama_command():
    try:
        subprocess.run(["ollama", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("❌ Ollama command not found. Please ensure Ollama is installed and available in PATH.")
        return False

# Function to stop Ollama
def stop_ollama():
    logger.info("🛑 Stopping Ollama...")
    try:
        subprocess.run(["ollama", "stop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout expired while stopping Ollama.")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error stopping Ollama: {e}")

# Function to start Ollama
def start_ollama():
    logger.info("🚀 Starting Ollama...")
    try:
        subprocess.run(["ollama", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout expired while starting Ollama.")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error starting Ollama: {e}")

# Function to check if the model is loaded
def check_model_loaded():
    try:
        output = subprocess.check_output(["ollama", "list"], text=True, timeout=10)
        return OLLAMA_MODEL in output or QUANTIZED_MODEL in output
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error checking model loaded: {e}")
        return False
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout expired while checking if model is loaded.")
        return False

# Function to run Ollama
def run_ollama():
    logger.info(f"🚀 Launching `{OLLAMA_MODEL}` model...")
    cmd = f"ollama run {OLLAMA_MODEL} {OLLAMA_ARGS}"
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Function to switch to quantized model
def switch_to_quantized():
    global OLLAMA_MODEL, OLLAMA_ARGS
    logger.info("⚡ Switching to quantized model (Q4_0) for stability...")
    OLLAMA_MODEL = QUANTIZED_MODEL
    OLLAMA_ARGS = "--n_ctx 4096"

# Create agents
def create_agents():
    logger.info("Creating agents...")
    agents = []
    for name in AGENT_NAMES:
        try:
            agent = autogen.AssistantAgent(name=name, llm_config={"model": OLLAMA_MODEL, "api_type": "ollama"})
            agents.append(agent)
        except Exception as e:
            logger.error(f"💥 Error creating agent {name}: {e}")
    return agents

# Function to collect data from gate.io
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

# Function to make trades on gate.io
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

# Run swarm execution with agents
def run_swarm():
    while True:
        try:
            agents = create_agents()
            if not agents:
                logger.error("💥 No agents created. Exiting swarm execution.")
                break
            groupchat = autogen.GroupChat(agents=agents, messages=[])
            controller = autogen.GroupChatManager(groupchat=groupchat)

            logger.info("🚀 Running AI agents...")
            asyncio.run(asyncio.gather(*[a.run(f"Task for {a.name}") for a in agents]))

            # Trader agent tasks
            data = collect_data_from_gate_io()
            if data:
                make_trade_on_gate_io()

            logger.info("✅ Task completed successfully!")
            break
        except Exception as e:
            logger.error(f"💥 Error during swarm execution: {e}\n🔄 Restarting in 3 seconds...")
            time.sleep(3)

# Main loop to initialize everything
def hyperloop():
    install_dependencies()

    # Check if required environment variables are set
    required_env_vars = ["OLLAMA_API_KEY", "OLLAMA_API_SECRET", "GATE_IO_API_KEY", "GATE_IO_API_SECRET"]
    for var in required_env_vars:
        if var not in os.environ:
            logger.error(f"❌ Required environment variable {var} is not set. Exiting.")
            return

    if not check_ollama_command():
        return

    stop_ollama()

    for attempt in range(1000):
        logger.info(f"🔁 [Attempt {attempt + 1}] Initializing system...")

        start_ollama()
        time.sleep(5)

        if check_model_loaded():
            logger.info("✅ Model loaded successfully!")
            run_swarm()
            break
        else:
            logger.warning("❌ Model failed to load. Retrying...")
            stop_ollama()
            time.sleep(3)

        if attempt == 5:
            switch_to_quantized()

hyperloop()
