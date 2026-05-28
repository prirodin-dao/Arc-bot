"""
Configuration for Arc Testnet Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Network Configuration
RPC_URL = "https://rpc.testnet.arc.network"
CHAIN_ID = 5042002
EXPLORER_URL = "https://explorer.testnet.arc.network"

# Contract Addresses (Arc Testnet)
CONTRACTS = {
    # Faucet URLs
    "FAUCET_URL": "https://faucet.circle.com/",
    "CIRCLE_API_FAUCET": "https://api.circle.com/v1/faucet/drips",
    
    # Tokens
    "USDC": "0x3600000000000000000000000000000000000000",
    "USDT": "0x2587521Ca49A69813991E9076B6eFbBb5CbfD19E",
    "USDY": "0x54D12437404aD9a4E7506C4497711b21CCE3ABCd",
    
    # StableSwap
    "STABLE_SWAP_ROUTER": "0xab9743e9715FFb5C5FC11Eb203937edA0C00c105",
    "STABLE_SWAP_POOL": "0xab9743e9715FFb5C5FC11Eb203937edA0C00c105",
    
    # Swap Interfaces (for Curve Finance, defi-on-arc)
    "CURVE_SWAP": "https://www.curve.finance/dex/arc/swap",
    "DEFI_SWAP": "https://defi-on-arc.netlify.app/",
    
    # NFT Contracts
    "NFT_OMNIHUB": "http://omnihub.xyz/create",  # NFT creation
    "NFT_ZKCODEX": "https://zkcodex.com/onchain/memorial",  # NFT minting
    
    # Deploy & Domains
    "ZKCODEX_DEPLOY": "https://zkcodex.com/onchain/deploy",
    "INFINITY_NAMES": "https://infinityname.com/",
    
    # GM
    "ONCHAIN_GM": "https://onchaingm.com/",
}

# API Endpoints (for non-browser operations)
API_ENDPOINTS = {
    "ZKCODEX_API": "https://api.zkcodex.com",  # If available
    "GM_API": "https://api.onchaingm.com",  # If available
}

# Bot Configuration
BOT_CONFIG = {
    "MIN_BALANCE": 0.001,  # Minimum ETH/USDC balance required
    "RETRY_ATTEMPTS": 3,
    "RETRY_DELAY": 5,  # seconds
    "WALLET_DELAY": 3,  # delay between wallets in seconds
    "OPERATION_DELAY": 2,  # delay between operations
    "REQUEST_TIMEOUT": 30,  # API request timeout
    "MAX_LOG_SIZE": 1_000_000_000,  # 1GB in bytes
    "LOG_BACKUP_COUNT": 5,
    "SCHEDULE_TIME": "00:00",  # Daily run time (HH:MM in UTC)
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

# Features to Enable/Disable
FEATURES = {
    "FAUCET": True,
    "SWAPS": True,
    "DEPLOY": True,
    "DOMAINS": True,
    "NFT": True,
    "GM": True,
}

# Operation Order (priority)
OPERATION_ORDER = [
    "faucet",
    "swaps",
    "deploy",
    "domains",
    "nft",
    "gm",
]

# Activity Timeouts (in seconds)
TIMEOUTS = {
    "faucet": 60,
    "swaps": 120,
    "deploy": 180,
    "domains": 90,
    "nft": 120,
    "gm": 45,
}

# ABI Snippets
ABIS = {
    "ERC20": [
        "function approve(address spender, uint256 amount) public returns (bool)",
        "function transfer(address to, uint256 amount) public returns (bool)",
        "function balanceOf(address account) public view returns (uint256)",
        "function allowance(address owner, address spender) public view returns (uint256)",
    ],
    "ROUTER": [
        "function swapExactTokensForTokens(address pool, bool zeroForOne, uint256 amountIn, uint256 minAmountOut) external returns (uint256)",
        "function addLiquidity(address pool, uint256 amount0, uint256 amount1, uint256 minLpOut) external returns (uint256)",
    ],
    "NFT": [
        "function mint(uint256 amount) external",
    ],
}
