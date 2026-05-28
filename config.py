"""
Configuration for Arc Testnet Bot (FULL + READY)
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Network Configuration
RPC_URL = "https://rpc.testnet.arc.network"
CHAIN_ID = 5042002
EXPLORER_URL = "https://explorer.testnet.arc.network"

# On‑chain Contracts (из твоего JS‑бота)
CONTRACTS = {
    # Tokens
    "USDC": "0x3600000000000000000000000000000000000000",
    "NFT": "0x632176D769aB950bb27cA00fDa81cfcb1886d082",
    "NAME_REGISTRY": "0x76a816EFa69e3183972ff7a231F5C8d7b065d9De",

    # Swap (заглушки — если нужны реальные, скажи)
    "ROUTER": "0x0000000000000000000000000000000000000000",
    "WETH":   "0x0000000000000000000000000000000000000000",
}

# ABI (из твоего JS‑бота)
ABIS = {
    "NFT": [
        "function mint(uint256 amount) external"
    ],
    "NAME_REGISTRY": [
        "function register(string name, address owner) external payable"
    ],
    "ERC20": [
        "function approve(address spender, uint256 amount) external returns (bool)",
        "function transfer(address to, uint256 amount) external returns (bool)",
        "function balanceOf(address account) external view returns (uint256)",
        "function allowance(address owner, address spender) external view returns (uint256)"
    ],
    "ROUTER": [
        "function swapExactTokensForTokens(address pool, bool zeroForOne, uint256 amountIn, uint256 minAmountOut) external returns (uint256)"
    ]
}

# Bot Configuration
BOT_CONFIG = {
    "MIN_BALANCE": 0.001,
    "RETRY_ATTEMPTS": 3,
    "RETRY_DELAY": 5,
    "WALLET_DELAY": 3,
    "OPERATION_DELAY": 2,
    "REQUEST_TIMEOUT": 30,
    "MAX_LOG_SIZE": 1_000_000_000,
    "LOG_BACKUP_COUNT": 5,
    "SCHEDULE_TIME": "00:00",

    # 👉 Эти параметры нужны для свапов и будут перезаписаны при запуске
    "SWAP_ETH_AMOUNT": 0.0005,
    "SWAP_USDC_AMOUNT": 1,
}

# Proxy Configuration
PROXY_CONFIG = {
    "USE_PROXIES": True,
    "PROXY_FILE": "proxy.txt",
    "PRIVATE_KEY_FILE": "private.txt",
}

# Logging
LOG_CONFIG = {
    "LOG_DIR": "logs",
    "LOG_FILE": "arc_bot.log",
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "DATE_FORMAT": "%Y-%m-%d %H:%M:%S",
}

# Features
FEATURES = {
    "FAUCET": True,
    "SWAPS": True,
    "DEPLOY": True,
    "DOMAINS": True,
    "NFT": True,
    "GM": True,
}

# Operation Order
OPERATION_ORDER = [
    "faucet",
    "swaps",
    "deploy",
    "domains",
    "nft",
    "gm",
]

# Timeouts
TIMEOUTS = {
    "faucet": 60,
    "swaps": 120,
    "deploy": 180,
    "domains": 90,
    "nft": 120,
    "gm": 45,
}
