# Swarm AI Trading Bot

## Overview

This project is a Swarm AI Trading Bot designed to interact with the gate.io API for data collection and trading. The bot uses multiple agents to perform various tasks, including data collection, trading, and more.

## Features

- **Dependency Management**: Automatically installs required packages.
- **Ollama Model Management**: Manages the Ollama model, including starting, stopping, and switching to a quantized model if necessary.
- **Agent Creation**: Creates multiple agents using the `autogen` library.
- **Swarm Execution**: Runs a swarm execution with the created agents.
- **Gate.io Integration**: Interacts with the gate.io API for data collection and trading.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/overor/1234.git
   cd 1234
   ```

2. Create a `.env` file in the root directory and add the following environment variables:
   ```sh
   OLLAMA_API_KEY=your_ollama_api_key
   OLLAMA_API_SECRET=your_ollama_api_secret
   GATE_IO_API_KEY=your_gate_io_api_key
   GATE_IO_API_SECRET=your_gate_io_api_secret
   ```

3. Run the `swarm.py` script:
   ```sh
   python swarm.py
   ```

## Usage

The main script `swarm.py` initializes the system, manages the Ollama model, and runs the swarm execution in a loop. The script includes functionality to interact with the gate.io API for data collection and trading.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
