"""
OnchainGM module — send GM transaction on ARC Testnet
"""

from web3 import Web3
from modules.logger import logger
from modules.wallet import wallet_manager
from modules.utils import get_retry_decorator
from config import CONTRACTS, ABIS


GM_ADDRESS = Web3.to_checksum_address(CONTRACTS["GM_CONTRACT"])
GM_ABI = ABIS["GM"]


class GMHandler:
    """Send GM transaction on OnchainGM contract"""

    @get_retry_decorator(max_attempts=3)
    def send_gm(self, wallet_index: int):
        try:
            w3 = wallet_manager.get_web3(wallet_index)
            account = wallet_manager.get_account(wallet_index)
            address = wallet_manager.get_wallet_address(wallet_index)

            if not w3 or not account:
                logger.error(f"[Wallet {wallet_index}] Web3/account unavailable")
                return False

            contract = w3.eth.contract(address=GM_ADDRESS, abi=GM_ABI)

            logger.info(f"[Wallet {wallet_index}] Sending GM...")

            nonce = w3.eth.get_transaction_count(address)
            gas_price = w3.eth.gas_price

            tx = contract.functions.sendGM().build_transaction({
                "from": address,
                "nonce": nonce,
                "gasPrice": gas_price,
                "gas": 200_000,
                "chainId": w3.eth.chain_id,
            })

            signed = w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

            logger.info(f"[Wallet {wallet_index}] TX sent: {tx_hash.hex()}")

            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            logger.success(f"[Wallet {wallet_index}] GM sent! Gas used: {receipt.gasUsed}")

            return True

        except Exception as e:
            logger.error(f"[Wallet {wallet_index}] GM failed: {e}")
            return False


gm_handler = GMHandler()
