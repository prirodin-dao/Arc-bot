"""
On-chain Contract Faucet Integration (No Circle API key required) - FULL READY
"""

import time
from web3 import Web3
from modules.logger import logger
from modules.wallet import wallet_manager
from config import CONTRACTS, ABIS, BOT_CONFIG
from modules.utils import get_retry_decorator


class FaucetHandler:
    def __init__(self):
        self.faucet_address = Web3.to_checksum_address(CONTRACTS["TEST_TOKEN_FAUCET"])
        self.faucet_abi = ABIS["ONCHAIN_FAUCET"]
        self.min_balance = BOT_CONFIG["MIN_BALANCE"]

    @get_retry_decorator(max_attempts=3)
    def claim_tokens(self, wallet_index):
        """Вызывает функцию claim() прямо в смарт-контракте бесплатного крана"""
        try:
            w3 = wallet_manager.get_web3(wallet_index)
            account = wallet_manager.get_account(wallet_index)
            address = wallet_manager.get_wallet_address(wallet_index)

            if not w3 or not account:
                logger.error(f"[Wallet {wallet_index + 1}] Web3 или аккаунт недоступны")
                return False

            # Проверка текущего баланса
            current_bal = wallet_manager.check_balance(wallet_index)
            if current_bal >= self.min_balance:
                logger.info(f"[Wallet {wallet_index + 1}] Баланс {current_bal} USDC уже достаточен. Кран пропущен.")
                return True

            logger.info(f"[Wallet {wallet_index + 1}] Запрашиваем 1000 tUSDC + tUSDT через ончейн-контракт крана...")

            faucet_contract = w3.eth.contract(address=self.faucet_address, abi=self.faucet_abi)
            
            nonce = w3.eth.get_transaction_count(address)
            gas_price = w3.eth.gas_price

            # Создание транзакции получения токенов
            tx = faucet_contract.functions.claim().build_transaction({
                "from": address,
                "nonce": nonce,
                "gasPrice": gas_price,
                "gas": 150_000,
                "chainId": w3.eth.chain_id
            })

            signed = w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
            
            logger.info(f"[Wallet {wallet_index + 1}] Транзакция крана отправлена в сеть: {tx_hash.hex()}")
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt.status == 1:
                logger.success(f"[Wallet {wallet_index + 1}] Кран успешно начислил токены! Gas used: {receipt.gasUsed}")
                return True
            else:
                logger.error(f"[Wallet {wallet_index + 1}] Контракт крана отклонил запрос (кулдаун 24 часа не прошел)")
                return False

        except Exception as e:
            logger.error(f"[Wallet {wallet_index + 1}] Не удалось получить токены из крана: {e}")
            return False


faucet_handler = FaucetHandler()
