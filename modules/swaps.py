"""
Swaps module — ARC Testnet Router swaps (USDC <-> EURC + fallback StableSwap) - FIXED DEADLINE
"""

import time
from web3 import Web3
from modules.logger import logger
from modules.wallet import wallet_manager
from modules.utils import get_retry_decorator
from config import CONTRACTS, ABIS


ROUTER = Web3.to_checksum_address(CONTRACTS["ROUTER"])
POOL = Web3.to_checksum_address(CONTRACTS["POOL"])

USDC = Web3.to_checksum_address(CONTRACTS["USDC"])
EURC = Web3.to_checksum_address(CONTRACTS["EURC"])

ROUTER_ABI = ABIS["ROUTER"]
POOL_ABI = ABIS["POOL"]
ERC20_ABI = ABIS["ERC20"]


class SwapHandler:
    """Perform swaps on ARC Router + StableSwap fallback"""

    def __init__(self):
        pass

    def _approve(self, w3, account, token, spender, amount):
        contract = w3.eth.contract(address=token, abi=ERC20_ABI)
        address = account.address

        nonce = w3.eth.get_transaction_count(address)
        gas_price = w3.eth.gas_price

        tx = contract.functions.approve(
            spender,
            amount
        ).build_transaction({
            "from": address,
            "nonce": nonce,
            "gasPrice": gas_price,
            "gas": 200_000,
            "chainId": w3.eth.chain_id
        })

        signed = w3.eth.account.sign_transaction(tx, account.key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)

    @get_retry_decorator(max_attempts=3)
    def swap_usdc_to_eurc(self, wallet_index, amount_in_usdc):
        try:
            w3 = wallet_manager.get_web3(wallet_index)
            account = wallet_manager.get_account(wallet_index)
            address = wallet_manager.get_wallet_address(wallet_index)

            if not w3 or not account:
                logger.error(f"[Wallet {wallet_index + 1}] Web3/account unavailable")
                return False

            amount_in = int(amount_in_usdc * 10**6)  # USDC 6 decimals
            
            logger.info(f"[Wallet {wallet_index + 1}] Approving USDC for Router...")
            self._approve(w3, account, USDC, ROUTER, amount_in)

            router = w3.eth.contract(address=ROUTER, abi=ROUTER_ABI)
            path = [USDC, EURC]

            amount_out_min = 0

            nonce = w3.eth.get_transaction_count(address)
            gas_price = w3.eth.gas_price

            # КРИТИЧЕСКИЙ ФИКС: Корректный Unix Timestamp дедлайна
            current_deadline = int(time.time()) + 1200  # Текущее время + 20 минут

            tx = router.functions.swapExactTokensForTokens(
                amount_in,
                amount_out_min,
                path,
                address,
                current_deadline  # <-- ИСПРАВЛЕНО
            ).build_transaction({
                "from": address,
                "nonce": nonce,
                "gasPrice": gas_price,
                "gas": 300_000,
                "chainId": w3.eth.chain_id,
            })

            signed = w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

            logger.info(f"[Wallet {wallet_index + 1}] Router Swap TX: {tx_hash.hex()}\")")
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt.status == 1:
                logger.success(f"[Wallet {wallet_index + 1}] Router Swap success! Gas used: {receipt.gasUsed}")
                return True
            
            logger.warning(f"[Wallet {wallet_index + 1}] Router Swap failed, trying StableSwap fallback...")
            return self.swap_stableswap_fallback(wallet_index, amount_in)

        except Exception as e:
            logger.error(f"[Wallet {wallet_index + 1}] Router Swap error: {e}. Trying StableSwap...")
            try:
                return self.swap_stableswap_fallback(wallet_index, int(amount_in_usdc * 10**6))
            except Exception as e2:
                logger.error(f"[Wallet {wallet_index + 1}] All swaps failed: {e2}")
                return False

    def swap_stableswap_fallback(self, wallet_index, amount_in):
        try:
            w3 = wallet_manager.get_web3(wallet_index)
            account = wallet_manager.get_account(wallet_index)
            address = wallet_manager.get_wallet_address(wallet_index)

            self._approve(w3, account, USDC, POOL, amount_in)
            pool = w3.eth.contract(address=POOL, abi=POOL_ABI)

            logger.info(f"[Wallet {wallet_index + 1}] Fallback StableSwap: USDC→EURC")

            dy = pool.functions.get_dy(0, 1, amount_in).call()
            min_dy = int(dy * 0.99)

            nonce = w3.eth.get_transaction_count(address)
            gas_price = w3.eth.gas_price

            tx = pool.functions.exchange(
                0, 1, amount_in, min_dy
            ).build_transaction({
                "from": address,
                "nonce": nonce,
                "gasPrice": gas_price,
                "gas": 300_000,
                "chainId": w3.eth.chain_id,
            })

            signed = w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

            logger.info(f"[Wallet {wallet_index + 1}] StableSwap TX: {tx_hash.hex()}")
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt.status == 1:
                logger.success(f"[Wallet {wallet_index + 1}] StableSwap success! Gas used: {receipt.gasUsed}")
                return True
            return False
        except Exception as e:
            logger.error(f"[Wallet {wallet_index + 1}] StableSwap failed: {e}")
            return False


swap_handler = SwapHandler()
