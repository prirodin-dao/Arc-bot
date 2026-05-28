"""
Swaps module — StableSwap Pool (USDC <-> USDT) - FULL READY
"""

import time
from web3 import Web3
from modules.logger import logger
from modules.wallet import wallet_manager
from modules.utils import get_retry_decorator
from config import CONTRACTS, ABIS

POOL = Web3.to_checksum_address(CONTRACTS["POOL"])
USDC = Web3.to_checksum_address(CONTRACTS["USDC"])
USDT = Web3.to_checksum_address(CONTRACTS["USDT"])

POOL_ABI = ABIS["POOL"]
ERC20_ABI = ABIS["ERC20"]


class SwapHandler:
    """Выполняет реальные обмены в стабильном пуле 1:1"""

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
            "gas": 100_000,
            "chainId": w3.eth.chain_id
        })

        signed = w3.eth.account.sign_transaction(tx, account.key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)

    @get_retry_decorator(max_attempts=3)
    def swap_usdc_to_eurc(self, wallet_index, amount_in_usdc):
        """Функция сохранила название для совместимости, но торгует в новом пуле USDC к USDT"""
        try:
            w3 = wallet_manager.get_web3(wallet_index)
            account = wallet_manager.get_account(wallet_index)
            address = wallet_manager.get_wallet_address(wallet_index)

            if not w3 or not account:
                logger.error(f"[Wallet {wallet_index + 1}] Web3 или аккаунт недоступны")
                return False

            amount_in = int(amount_in_usdc * 10**6)  # 6 знаков после запятой у USDC
            
            logger.info(f"[Wallet {wallet_index + 1}] Даем разрешение пулу (Approve) на трату USDC...")
            self._approve(w3, account, USDC, POOL, amount_in)

            pool = w3.eth.contract(address=POOL, abi=POOL_ABI)

            # Считаем сколько должны получить (0 = USDC, 1 = USDT)
            dy = pool.functions.get_dy(0, 1, amount_in).call()
            min_dy = int(dy * 0.98)  # Проскальзывание 2%

            nonce = w3.eth.get_transaction_count(address)
            gas_price = w3.eth.gas_price

            logger.info(f"[Wallet {wallet_index + 1}] Выполняем обмен в StableSwap: {amount_in_usdc} USDC -> USDT")

            tx = pool.functions.exchange(
                0, 1, amount_in, min_dy
            ).build_transaction({
                "from": address,
                "nonce": nonce,
                "gasPrice": gas_price,
                "gas": 250_000,
                "chainId": w3.eth.chain_id,
            })

            signed = w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

            logger.info(f"[Wallet {wallet_index + 1}] Транзакция обмена отправлена: {tx_hash.hex()}")
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt.status == 1:
                logger.success(f"[Wallet {wallet_index + 1}] Обмен завершен успешно! Использовано газа: {receipt.gasUsed}")
                return True
            
            logger.error(f"[Wallet {wallet_index + 1}] Транзакция обмена была отклонена сетью.")
            return False

        except Exception as e:
            logger.error(f"[Wallet {wallet_index + 1}] Ошибка во время обмена в StableSwap: {e}")
            return False


swap_handler = SwapHandler()
