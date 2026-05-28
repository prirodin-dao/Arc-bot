"""
Proxy manager — assigns proxies to wallets - FIXED
"""

from modules.wallet import wallet_manager
from modules.logger import logger
from config import PROXY_CONFIG


class ProxyManager:
    def __init__(self):
        self.proxies = wallet_manager.proxies

    def get_proxy_for_wallet(self, wallet_index: int):
        if not PROXY_CONFIG["USE_PROXIES"] or not self.proxies:
            return None

        proxy = self.proxies[wallet_index % len(self.proxies)]
        logger.debug(f"[ProxyManager] Wallet {wallet_index + 1} → Proxy {proxy}")
        return proxy

    def get_requests_proxy(self, wallet_index: int):
        """Возвращает словарь прокси для библиотеки requests"""
        proxy = self.get_proxy_for_wallet(wallet_index)
        if proxy:
            return {"http": proxy, "https": proxy}
        return None


proxy_manager = ProxyManager()
