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
AGENT_NAMES = ["Scout", "Editor", "Uploader", "Clicker", "Transaction"]
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

# Function to stop Ollama
def stop_ollama():
    logger.info("🛑 Stopping Ollama...")
    subprocess.run(["ollama", "stop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Function to start Ollama
def start_ollama():
    logger.info("🚀 Starting Ollama...")
    subprocess.run(["ollama", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Function to check if the model is loaded
def check_model_loaded():
    try:
        output = subprocess.check_output(["ollama", "list"], text=True)
        return OLLAMA_MODEL in output or QUANTIZED_MODEL in output
    except subprocess.CalledProcessError:
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

            logger.info("✅ Task completed successfully!")
            break
        except Exception as e:
            logger.error(f"💥 Error during swarm execution: {e}\n🔄 Restarting in 3 seconds...")
            time.sleep(3)

# Function to get all tradable symbols
def get_all_symbols():
    url = 'https://api.gateio.ws/api/v4/spot/currency_pairs'
    response = requests.get(url)
    data = response.json()
    symbols = []
    for pair in data:
        if pair['trade_status'] == 'tradable':
            symbols.append({
                'id': pair['id'],
                'min_amount': float(pair['min_quote_amount']),
                'precision': pair['amount_precision'],
            })
    return symbols

# Function to estimate profit per trade
def estimate_profit(symbol):
    url = f'https://api.gateio.ws/api/v4/spot/order_book?currency_pair={symbol}&limit=5'
    response = requests.get(url)
    order_book = response.json()
    
    highest_bid = float(order_book['bids'][0][0])
    lowest_ask = float(order_book['asks'][0][0])

    spread = lowest_ask - highest_bid
    profit_per_trade = spread

    return profit_per_trade

# Main loop to initialize everything
def hyperloop():
    install_dependencies()
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

    all_symbols = get_all_symbols()
    print(f"Found {len(all_symbols)} symbols")
    
    for symbol_info in all_symbols:
        symbol = symbol_info['id']
        min_amount = symbol_info['min_amount']
        
        profit = estimate_profit(symbol)
        if profit > 0.01:  # 1 cent threshold
            print(f"[🚀] {symbol} meets profit criteria! Estimated profit: ${profit:.5f}/sec")
            # Here you would start grid trading logic
        else:
            print(f"[x] {symbol} skipped. Profit only: ${profit:.5f}/sec")
        
        time.sleep(0.2)  # Respect rate limits

hyperloop()
