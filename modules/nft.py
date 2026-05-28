"""
Real NFT minting module for ARC Testnet
"""

from web3 import Web3
from modules.logger import logger
from modules.wallet import wallet_manager
from modules.utils import get_retry_decorator, rate_limiter, delay
from config import CONTRACTS, ABIS, BOT_CONFIG

NFT_ADDRESS = Web3.to_checksum_address(CONTRACTS["NFT_OMNIHUB"]) \
    if CONTRACTS["NFT_OMNIHUB"].startswith("0x") else None

NFT_ABI = ABIS["NFT"]


class NFTHandler:
    def __init__(self):
        self.timeout = BOT_CONFIG["REQUEST_TIMEOUT"]

    @get_retry_decorator(max_attempts=3)
    def mint_nft(self, wallet_index, amount=1):
        """Mint NFT on ARC Testnet"""
        try:
            w3 = wallet_manager.get_web3(wallet_index)
            account = wallet_manager.get_account(wallet_index)
            address = wallet_manager.get_wallet_address(wallet_index)

            if not w3 or not account:
                logger.error(f"[Wallet {wallet_index}] Web3/account unavailable")
                return False

            if not NFT_ADDRESS:
                logger.error("NFT contract address missing in config")
                return False

            contract = w3.eth.contract(address=NFT_ADDRESS, abi=NFT_ABI)

            logger.info(f"[Wallet {wallet_index}] Minting {amount} NFT(s)")

            nonce = w3.eth.get_transaction_count(address)
            gas_price = w3.eth.gas_price

            tx = contract.functions.mint(amount).build_transaction({
                "from": address,
                "nonce": nonce,
                "gasPrice": gas_price,
                "gas": 300_000,
            })

            signed = w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

            logger.info(f"[Wallet {wallet_index}] TX sent: {tx_hash.hex()}")

            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            logger.success(f"[Wallet {wallet_index}] NFT minted! Gas used: {receipt.gasUsed}")

            return True

        except Exception as e:
            logger.error(f"[Wallet {wallet_index}] NFT mint failed: {e}")
            return False


nft_handler = NFTHandler()
