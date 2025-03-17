#!/bin/bash

echo "Starting Ollama..."
ollama serve & sleep 5  # Start the server

# Ensure Llama3.2 model is downloaded once
if [ ! -f "/root/.ollama/llama3.2" ]; then
    echo "Downloading Llama3.2..."
    ollama pull llama3.2
fi

echo "Ollama is ready!"
tail -f /dev/null  # Keep container running
