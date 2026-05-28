"""
Configuration for Arc Testnet Bot (UPDATED WITH NEW CONTRACTS) - FULL READY
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
# On‑chain Contracts (Свежие адреса из нового репозитория)
# ============================================================

CONTRACTS = {
    # Токены из нового рабочего репозитория
    "USDC": "0x53646C53e712cE320182E289E7364d4d0e4D6D01",
    "USDT": "0x2587521Ca49A69813991E9076B6eFbBb5CbfD19E",
    
    # Новый бесплатный контракт крана (дает 1000 USDC + 1000 USDT)
    "TEST_TOKEN_FAUCET": "0x1809123f52ebE8f80e328D99a16Ee42D679B2bA6",

    # Обновленный пул для обменов (DEX StableSwap)
    "POOL": "0xab9743e9715FFb5C5FC11Eb203937edA0C00c105",

    # Контракты для остальных активностей
    "NFT_OMNIHUB": "0x632176D769aB950bb27cA00fDa81cfcb1886d082",
    "INFINITY_NAME": "0x76a816EFa69e3183972ff7a231F5C8d7b065d9De",
    "GM_CONTRACT": "0x401E5037DeDD7eF171050A48BF9fbC36cBA0974E",
    "ROUTER": "0x51E289a54Fd85f6DB7950bd1f8aDE71c4c11FF1F",
    
    "TOKEN_BYTECODE": "0x608060403261000f565b6100c1565b61001d6100183660006100df565b60046101c1565b610332565b60405161002b91906104ca565b60405180910390f35b60405161003f919061053b565b60405180910390f3"
}

# ============================================================
# ABIs (Интерфейсы для взаимодействия со смарт-контрактами)
# ============================================================

ABIs = {
    "ERC20": [
        {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
        {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "success", "type": "bool"}], "type": "function"}
    ],
    "POOL": [
        {"inputs": [{"internalType": "int128", "name": "i", "type": "int128"}, {"internalType": "int128", "name": "j", "type": "int128"}, {"internalType": "uint256", "name": "dx", "type": "uint256"}], "name": "get_dy", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
        {"inputs": [{"internalType": "int128", "name": "i", "type": "int128"}, {"internalType": "int128", "name": "j", "type": "int128"}, {"internalType": "uint256", "name": "dx", "type": "uint256"}, {"internalType": "uint256", "name": "min_dy", "type": "uint256"}], "name": "exchange", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "nonpayable", "type": "function"}
    ],
    "ONCHAIN_FAUCET": [
        {"inputs": [], "name": "claim", "outputs": [], "stateMutability": "nonpayable", "type": "function"}
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
    "MIN_BALANCE": 10.0,          # Пропускаем кран, если баланс больше 10 USDC
    "REQUEST_TIMEOUT": 30,
    "RETRY_ATTEMPTS": 3,
    "MAX_LOG_SIZE": 1024 * 1024 * 1024,
    "LOG_BACKUP_COUNT": 5,
    "SCHEDULE_TIME": "00:00",
    "SWAP_USDC_AMOUNT": 10,        # Сумма для обмена USDC -> USDT
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
