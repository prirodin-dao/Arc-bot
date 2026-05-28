"""
Real Circle Faucet integration for ARC Testnet - FIXED PROXY LEAK
"""

import time
import requests
from modules.logger import logger
from modules.wallet import wallet_manager
from config import CONTRACTS, BOT_CONFIG
from modules.utils import get_retry_decorator, rate_limiter
import os


class FaucetHandler:
    def __init__(self):
        self.api_url = CONTRACTS["CIRCLE_API_FAUCET"]
        self.web_url = CONTRACTS["FAUCET_URL"]
        self.chain = "ARC_TESTNET"
        self.api_key = os.getenv("CIRCLE_API_KEY")
        self.min_balance = BOT_CONFIG["MIN_BALANCE"]
        self.rate_limit_wait = 1800  # 30 minutes

        self.last_claim_time = {}

    def _can_claim(self, wallet_index):
        last = self.last_claim_time.get(wallet_index)
        if not last:
            return True

        elapsed = time.time() - last
        if elapsed < self.rate_limit_wait:
            wait_min = int((self.rate_limit_wait - elapsed) / 60)
            logger.warning(
                f"[Wallet {wallet_index + 1}] Faucet rate limit active, wait {wait_min} min"
            )
            return False

        return True

    @get_retry_decorator(max_attempts=3)
    def claim_tokens(self, wallet_index):
        """Claim USDC from Circle Faucet via Proxy"""
        address = wallet_manager.get_wallet_address(wallet_index)
        
        # Сначала проверяем текущий баланс
        current_bal = wallet_manager.check_balance(wallet_index)
        if current_bal >= self.min_balance:
            logger.info(f"[Wallet {wallet_index + 1}] Balance {current_bal} USDC >= Min {self.min_balance}. Faucet skipped.")
            return True

        if not self._can_claim(wallet_index):
            return False

        if not self.api_key:
            logger.error(
                f"[Wallet {wallet_index + 1}] No CIRCLE_API_KEY in .env — faucet cannot work automatically"
            )
            logger.info(f"Manual faucet URL: {self.web_url}")
            return False

        payload = {
            "address": address,
            "chain": self.chain,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        logger.info(f"[Wallet {wallet_index + 1}] Requesting faucet for {address}")

        rate_limiter.wait()

        try:
            # КРИТИЧЕСКИЙ ФИКС: Запрос к API крана идет строго через прокси кошелька
            from modules.proxy_manager import proxy_manager
            wallet_proxy = proxy_manager.get_requests_proxy(wallet_index)

            response = requests.post(
                self.api_url, json=payload, headers=headers, proxies=wallet_proxy, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(
                    f"[Wallet {wallet_index + 1}] Faucet success: dripId={data.get('data', {}).get('dripId')}"
                )
                self.last_claim_time[wallet_index] = time.time()
                return True

            logger.error(
                f"[Wallet {wallet_index + 1}] Faucet error {response.status_code}: {response.text}"
            )
            return False

        except Exception as e:
            logger.error(f"[Wallet {wallet_index + 1}] Faucet request failed: {e}")
            return False


faucet_handler = FaucetHandler()
