#!/bin/bash

set -e

# Define constants
KEYRING_BACKEND="test"
HOME_DIR="/data/.allorad"
ENV_FILE="/data/env_file"

# Check if the account already exists
if allorad keys --home="$HOME_DIR" --keyring-backend "$KEYRING_BACKEND" show "$NAME" > /dev/null 2>&1; then
    echo "Allora account: $NAME already imported"
else
    echo "Creating Allora account: $NAME"
    
    # Add the account and capture output
    output=$(allorad keys add "$NAME" --home="$HOME_DIR" --keyring-backend "$KEYRING_BACKEND" 2>&1)
    address=$(echo "$output" | grep 'address:' | awk '{print $2}')
    mnemonic=$(echo "$output" | tail -n 1)
    
    # Parse and update the JSON string
    updated_json=$(echo "$ALLORA_OFFCHAIN_NODE_CONFIG_JSON" | jq --arg name "$NAME" --arg mnemonic "$mnemonic" '
    .wallet.addressKeyName = $name |
    .wallet.addressRestoreMnemonic = $mnemonic
    ')
    
    # Save updated JSON and environment variables
    echo "ALLORA_OFFCHAIN_NODE_CONFIG_JSON=$(echo "$updated_json" | jq -c .)" > "$ENV_FILE"
    echo "ALLORA_OFFCHAIN_ACCOUNT_ADDRESS=$address" >> "$ENV_FILE"
    echo "NAME=$NAME" >> "$ENV_FILE"
    
    echo "Updated ALLORA_OFFCHAIN_NODE_CONFIG_JSON saved to $ENV_FILE"
fi

# Update ENV_LOADED status
if grep -q "ENV_LOADED=false" "$ENV_FILE"; then
    sed -i 's/ENV_LOADED=false/ENV_LOADED=true/' "$ENV_FILE"
else
    echo "ENV_LOADED=true" >> "$ENV_FILE"
fi
