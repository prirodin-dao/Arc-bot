"""
Real token deployment module for ARC Testnet
"""

from web3 import Web3
from modules.logger import logger
from modules.wallet import wallet_manager
from modules.utils import get_retry_decorator
from config import CONTRACTS, BOT_CONFIG

# Добавь TOKEN_BYTECODE в config.py
TOKEN_BYTECODE = CONTRACTS["TOKEN_BYTECODE"]
CREATION_FEE_WEI = int(0.000037 * 1e18)  # 0.000037 ETH как в JS‑боте


class DeployHandler:
    """Deploy ERC‑20 token on ARC Testnet"""

    @get_retry_decorator(max_attempts=3)
    def deploy_contract(self, wallet_index, name=None, symbol=None, supply=1_000_000):
        try:
            w3 = wallet_manager.get_web3(wallet_index)
            account = wallet_manager.get_account(wallet_index)
            address = wallet_manager.get_wallet_address(wallet_index)

            if not w3 or not account:
                logger.error(f"[Wallet {wallet_index}] Web3/account unavailable")
                return False

            # Defaults
            if name is None:
                name = f"Token{wallet_index}"
            if symbol is None:
                symbol = f"T{wallet_index}"

            logger.info(f"[Wallet {wallet_index}] Deploying token {name} ({symbol})")

            # Encode constructor params
            encoded = w3.codec.encode_abi(
                ["string", "string", "uint256"],
                [name, symbol, Web3.to_wei(supply, "ether")]
            )

            # Build final bytecode
            deploy_data = TOKEN_BYTECODE + encoded.hex()

            nonce = w3.eth.get_transaction_count(address)
            gas_price = w3.eth.gas_price

            tx = {
                "from": address,
                "nonce": nonce,
                "gasPrice": gas_price,
                "gas": 1_500_000,
                "value": CREATION_FEE_WEI,
                "data": deploy_data,
                "chainId": w3.eth.chain_id,
            }

            signed = w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

            logger.info(f"[Wallet {wallet_index}] TX sent: {tx_hash.hex()}")

            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            contract_address = receipt.contractAddress
            logger.success(f"[Wallet {wallet_index}] Token deployed at: {contract_address}")
            logger.info(f"[Wallet {wallet_index}] Gas used: {receipt.gasUsed}")

            return contract_address

        except Exception as e:
            logger.error(f"[Wallet {wallet_index}] Deploy failed: {e}")
            return False


deploy_handler = DeployHandler()
