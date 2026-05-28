"""
Configuration for Arc Testnet Bot (FULL + READY) - FIXED
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
# On‑chain Contracts
# ============================================================

CONTRACTS = {
    # Tokens
    "USDC": "0x3600000000000000000000000000000000000000",
    "EURC": "0x89B50855Aa3bE2F677cD6303Cec089B5F319D72a",
    "WETH": "0x19CF35858dd6Db905Ddba09eaF25478a592e31ef",

    # Названия исправлены под вызовы в модулях nft.py и domains.py
    "NFT_OMNIHUB": "0x632176D769aB950bb27cA00fDa81cfcb1886d082",
    "INFINITY_NAME": "0x76a816EFa69e3183972ff7a231F5C8d7b065d9De",

    "GM_CONTRACT": "0x401E5037DeDD7eF171050A48BF9fbC36cBA0974E",
    "ROUTER": "0x51E289a54Fd85f6DB7950bd1f8aDE71c4c11FF1F",
    "FACTORY": "0x6F4902cdFfC0dfe539cdC3019147383C458f0FBe8",
    "POOL": "0x181DA777C301Bc37B078DEf57569685678e59eD0",

    "CIRCLE_API_FAUCET": "https://api.circle.com/v1/faucets/drips",
    "FAUCET_URL": "https://faucet.circle.com/",
    "TOKEN_BYTECODE": "0x608060403261000f565b6100c1565b61001d6100183660006100df565b60046101c1565b610332565b60405161002b91906104ca565b60405180910390f35b60405161003f919061053b565b60405180910390f3"
}

# ============================================================
# ABIs (Минимальные интерфейсы для экономии места)
# ============================================================

ABIs = {
    "ERC20": [
        {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
        {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "success", "type": "bool"}], "type": "function"}
    ],
    "ROUTER": [
        {"inputs": [{"internalType": "uint256", "name": "amountIn", "type": "uint256"}, {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"}, {"internalType": "address[]", "name": "path", "type": "address[]"}, {"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "deadline", "type": "uint256"}], "name": "swapExactTokensForTokens", "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}], "stateMutability": "nonpayable", "type": "function"}
    ],
    "POOL": [
        {"inputs": [{"internalType": "int128", "name": "i", "type": "int128"}, {"internalType": "int128", "name": "j", "type": "int128"}, {"internalType": "uint256", "name": "dx", "type": "uint256"}], "name": "get_dy", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
        {"inputs": [{"internalType": "int128", "name": "i", "type": "int128"}, {"internalType": "int128", "name": "j", "type": "int128"}, {"internalType": "uint256", "name": "dx", "type": "uint256"}, {"internalType": "uint256", "name": "min_dy", "type": "uint256"}], "name": "exchange", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "nonpayable", "type": "function"}
    ],
    "NFT": [
        {"inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "mint", "outputs": [], "stateMutability": "nonpayable", "type": "function"}
    ],
    "NAME_REGISTRY": [
        {"inputs": [{"internalType": "string", "name": "name", "type": "string"}, {"internalType": "address", "name": "resolver", "type": "address"}], "name": "register", "outputs": [], "stateMutability": "payable", "type": "function"}
    ],
    "GM": [
        {"inputs": [], "name": "sendGM", "outputs": [], "stateMutability": "nonpayable", "type": "function"}
    ]
}

# ============================================================
# Global Bot Settings
# ============================================================

BOT_CONFIG = {
    "MIN_BALANCE": 0.5,           # Критический фикс: необходим для работы faucet.py
    "REQUEST_TIMEOUT": 30,
    "RETRY_ATTEMPTS": 3,
    "MAX_LOG_SIZE": 1024 * 1024 * 1024,
    "LOG_BACKUP_COUNT": 5,
    "SCHEDULE_TIME": "00:00",
    "SWAP_USDC_AMOUNT": 5,
    "SWAP_SLIPPAGE": 1.0,
}

PROXY_CONFIG = {
    "USE_PROXIES": True,
    "PROXY_FILE": "proxy.txt",
    "PRIVATE_KEY_FILE": "private.txt",
}

LOG_CONFIG = {
    "LOG_DIR": "logs",
    "LOG_FILE": "arc_bot.log",
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "DATE_FORMAT": "%Y-%m-%d %H:%M:%S",
}

FEATURES = {
    "FAUCET": True,
    "SWAPS": True,
    "DEPLOY": True,
    "DOMAINS": True,
    "NFT": True,
    "GM": True,
}

OPERATION_ORDER = ["faucet", "swaps", "deploy", "domains", "nft", "gm"]
TIMEOUTS = {"faucet_delay": 5, "tx_timeout": 60}
