"""
Wallet management module - FIXED PROXY & DECIMALS
"""
import os
from web3 import Web3
from eth_account import Account
from config import RPC_URL, CHAIN_ID, PROXY_CONFIG
from modules.logger import logger

class WalletManager:
    """Manage wallets and connections"""
    
    def __init__(self):
        self.rpc_url = RPC_URL
        self.chain_id = CHAIN_ID
        self.wallets = []
        self.proxies = []
        self.load_wallets()
        self.load_proxies()
    
    def load_wallets(self):
        """Load private keys from private.txt"""
        try:
            private_key_file = PROXY_CONFIG["PRIVATE_KEY_FILE"]
            
            if not os.path.exists(private_key_file):
                logger.error(f"Private key file not found: {private_key_file}")
                return
            
            with open(private_key_file, "r") as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                try:
                    if not line.startswith("0x"):
                        line = "0x" + line
                    
                    account = Account.from_key(line)
                    self.wallets.append({
                        "index": i,
                        "private_key": line,
                        "address": account.address,
                        "account": account
                    })
                except Exception as e:
                    logger.error(f"Error loading private key on line {i+1}: {e}")
            
            logger.info(f"Successfully loaded {len(self.wallets)} wallets")
        except Exception as e:
            logger.error(f"Error loading wallets: {e}")

    def load_proxies(self):
        """Load proxies from proxy.txt"""
        try:
            proxy_file = PROXY_CONFIG["PROXY_FILE"]
            if not os.path.exists(proxy_file):
                logger.warning(f"Proxy file not found: {proxy_file}. Running without proxies.")
                return
            
            with open(proxy_file, "r") as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    if not line.startswith("http://") and not line.startswith("https://"):
                        line = "http://" + line
                    self.proxies.append(line)
                    
            logger.info(f"Successfully loaded {len(self.proxies)} proxies")
        except Exception as e:
            logger.error(f"Error loading proxies: {e}")
    
    def get_web3(self, wallet_index):
        """Get Web3 instance with strict proxy enforcement for v7.0.0"""
        try:
            if PROXY_CONFIG["USE_PROXIES"] and self.proxies:
                proxy = self.proxies[wallet_index % len(self.proxies)]
                
                # КРИТИЧЕСКИЙ ФИКС: В Web3 v7 прокси передаются строго внутрь HTTPProvider
                provider = Web3.HTTPProvider(
                    self.rpc_url,
                    request_kwargs={
                        "proxies": {"http": proxy, "https": proxy},
                        "timeout": 30
                    }
                )
                return Web3(provider)
            else:
                return Web3(Web3.HTTPProvider(self.rpc_url))
        
        except Exception as e:
            logger.error(f"Error creating Web3 instance for wallet {wallet_index}: {str(e)}")
            return None
    
    def get_account(self, wallet_index):
        if wallet_index < len(self.wallets):
            return self.wallets[wallet_index]["account"]
        return None
    
    def get_wallet_address(self, wallet_index):
        if wallet_index < len(self.wallets):
            return self.wallets[wallet_index]["address"]
        return None
    
    def check_balance(self, wallet_index):
        """Check wallet balance (Native USDC on Arc Testnet)"""
        try:
            w3 = self.get_web3(wallet_index)
            if not w3:
                return 0
            
            address = self.get_wallet_address(wallet_index)
            balance_wei = w3.eth.get_balance(address)
            
            # КРИТИЧЕСКИЙ ФИКС: Деление на 10**6, так как токен газа — USDC с 6 знаками
            balance_usdc = balance_wei / 10**6
            
            logger.debug(f"Wallet {wallet_index + 1} balance: {balance_usdc} USDC")
            return float(balance_usdc)
        
        except Exception as e:
            logger.error(f"Error checking balance for wallet {wallet_index + 1}: {str(e)}")
            return 0
    
    @property
    def wallet_count(self):
        return len(self.wallets)

wallet_manager = WalletManager()
