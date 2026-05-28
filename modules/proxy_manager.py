"""
Proxy manager — assigns proxies to wallets
"""

from modules.wallet import wallet_manager
from modules.logger import logger


class ProxyManager:
    def __init__(self):
        self.proxies = wallet_manager.proxies

    def get_proxy_for_wallet(self, wallet_index: int):
        if not self.proxies:
            return None

        proxy = self.proxies[wallet_index % len(self.proxies)]
        logger.debug(f"[ProxyManager] Wallet {wallet_index} → Proxy {proxy}")
        return proxy


proxy_manager = ProxyManager()
