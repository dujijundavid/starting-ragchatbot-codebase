#!/bin/bash

echo "=== Fixing .env file permissions ==="

if [ -f ".env" ]; then
    echo "Found .env file"
    echo "Current permissions:"
    ls -la .env
    
    echo ""
    echo "Fixing permissions..."
    chmod 644 .env
    
    echo "New permissions:"
    ls -la .env
    echo "✓ Done"
else
    echo "⚠️  .env file not found in current directory"
    echo "Please create one with:"
    echo "  echo 'LLM_PROVIDER=deepseek' > .env"
    echo "  echo 'DEEPSEEK_API_KEY=your_key_here' >> .env"
fi

