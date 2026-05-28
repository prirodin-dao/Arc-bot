"""
Configuration for Arc Testnet Bot (FULL + READY)
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# Network Configuration
# ============================================================

RPC_URL = "https://rpc.testnet.arc.network"
CHAIN_ID = 5042002
EXPLORER_URL = "https://explorer.testnet.arc.network"

# ============================================================
# On‑chain Contracts (JS‑бот + реальные DEX адреса)
# ============================================================

CONTRACTS = {
    # Tokens
    "USDC": "0x3600000000000000000000000000000000000000",
    "EURC": "0x89B50855Aa3bE2F677cD6303Cec089B5F319D72a",
    "WETH": "0x19CF35858dd6Db905Ddba09eaF25478a592e31ef",

    # Your JS bot contracts
    "NFT": "0x632176D769aB950bb27cA00fDa81cfcb1886d082",
    "NAME_REGISTRY": "0x76a816EFa69e3183972ff7a231F5C8d7b065d9De",

    # REAL Arc Testnet DEX (Uniswap‑style)
    "ROUTER": "0x51E289a54Fd85f6DB7950bd1f8aDE71c4c11FF1F",
    "FACTORY": "0x6F4902cdFfC0dfe539cdC3019147383C458f0FBe8",

    # REAL StableSwap Pool (USDC/EURC)
    "POOL": "0x181DA777C301Bc37B078DEf57569685678e59eD0",
}

# ============================================================
# ABI
# ============================================================

ABIS = {
    # NFT mint
    "NFT": [
        "function mint(uint256 amount) external"
    ],

    # Domain registry
    "NAME_REGISTRY": [
        "function register(string name, address owner) external payable"
    ],

    # ERC‑20
    "ERC20": [
        "function approve(address spender, uint256 amount) external returns (bool)",
        "function transfer(address to, uint256 amount) external returns (bool)",
        "function balanceOf(address account) external view returns (uint256)",
        "function allowance(address owner, address spender) external view returns (uint256)",
        "function decimals() external view returns (uint8)"
    ],

    # Uniswap‑style Router
    "ROUTER": [
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "swapExactTokensForTokens",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"}
            ],
            "name": "getAmountsOut",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "view",
            "type": "function"
        }
    ],

    # StableSwap Pool (Curve‑style)
    "POOL": [
        {
            "inputs": [
                {"internalType": "int128", "name": "i", "type": "int128"},
                {"internalType": "int128", "name": "j", "type": "int128"},
                {"internalType": "uint256", "name": "dx", "type": "uint256"},
                {"internalType": "uint256", "name": "min_dy", "type": "uint256"}
            ],
            "name": "exchange",
            "outputs": [{"internalType": "uint256", "name": "dy", "type": "uint256"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "int128", "name": "i", "type": "int128"},
                {"internalType": "int128", "name": "j", "type": "int128"},
                {"internalType": "uint256", "name": "dx", "type": "uint256"}
            ],
            "name": "get_dy",
            "outputs": [{"internalType": "uint256", "name": "dy", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]
}

# ============================================================
# Bot Configuration
# ============================================================

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

    # Swap amounts (теперь реальные)
    "SWAP_USDC_AMOUNT": 5,
    "SWAP_SLIPPAGE": 1.0,
}

# ============================================================
# Proxy Configuration
# ============================================================

PROXY_CONFIG = {
    "USE_PROXIES": True,
    "PROXY_FILE": "proxy.txt",
    "PRIVATE_KEY_FILE": "private.txt",
}

# ============================================================
# Logging
# ============================================================

LOG_CONFIG = {
    "LOG_DIR": "logs",
    "LOG_FILE": "arc_bot.log",
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "DATE_FORMAT": "%Y-%m-%d %H:%M:%S",
}

# ============================================================
# Features
# ============================================================

FEATURES = {
    "FAUCET": True,
    "SWAPS": True,
    "DEPLOY": True,
    "DOMAINS": True,
    "NFT": True,
    "GM": True,
}

# ============================================================
# Operation Order
# ============================================================

OPERATION_ORDER = [
    "faucet",
    "swaps",
    "deploy",
    "domains",
    "nft",
    "gm",
]

# ============================================================
# Timeouts
# ============================================================

TIMEOUTS = {
    "faucet": 60,
    "swaps": 120,
    "deploy": 180,
    "domains": 90,
    "nft": 120,
    "gm": 45,
}
