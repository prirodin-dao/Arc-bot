"""
Real Infinity Name domain registration for ARC Testnet
"""

from web3 import Web3
from modules.logger import logger
from modules.wallet import wallet_manager
from modules.utils import get_retry_decorator
from config import CONTRACTS, ABIS, BOT_CONFIG

NAME_REGISTRY = Web3.to_checksum_address(CONTRACTS["INFINITY_NAME"])
NAME_ABI = ABIS["NAME_REGISTRY"]

ONE_ETH = Web3.to_wei(1, "ether")  # как в JS‑боте


class DomainsHandler:
    """Register domains on Infinity Name"""

    @get_retry_decorator(max_attempts=3)
    def register_domain(self, wallet_index, name: str):
        try:
            w3 = wallet_manager.get_web3(wallet_index)
            account = wallet_manager.get_account(wallet_index)
            address = wallet_manager.get_wallet_address(wallet_index)

            if not w3 or not account:
                logger.error(f"[Wallet {wallet_index}] Web3/account unavailable")
                return False

            contract = w3.eth.contract(address=NAME_REGISTRY, abi=NAME_ABI)

            logger.info(f"[Wallet {wallet_index}] Registering domain: {name}")

            nonce = w3.eth.get_transaction_count(address)
            gas_price = w3.eth.gas_price

            tx = contract.functions.register(
                name,
                "0x0000000000000000000000000000000000000000"
            ).build_transaction({
                "from": address,
                "nonce": nonce,
                "gasPrice": gas_price,
                "gas": 300_000,
                "value": ONE_ETH,
                "chainId": w3.eth.chain_id,
            })

            signed = w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

            logger.info(f"[Wallet {wallet_index}] TX sent: {tx_hash.hex()}")

            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            logger.success(f"[Wallet {wallet_index}] Domain registered! Gas used: {receipt.gasUsed}")

            return True

        except Exception as e:
            logger.error(f"[Wallet {wallet_index}] Domain registration failed: {e}")
            return False


domains_handler = DomainsHandler()
