"""
Wallet management module
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
                    # Ensure it's a valid hex string
                    if not line.startswith("0x"):
                        line = "0x" + line
                    
                    account = Account.from_key(line)
                    self.wallets.append({
                        "index": i,
                        "private_key": line,
                        "address": account.address,
                        "account": account
                    })
                    logger.debug(f"Loaded wallet {i}: {account.address}")
                except Exception as e:
                    logger.error(f"Invalid private key at line {i}: {str(e)}")
            
            logger.info(f"Loaded {len(self.wallets)} wallets")
        
        except Exception as e:
            logger.error(f"Error loading wallets: {str(e)}")
    
    def load_proxies(self):
        """Load proxies from proxy.txt"""
        try:
            proxy_file = PROXY_CONFIG["PROXY_FILE"]
            
            if not os.path.exists(proxy_file):
                logger.warning(f"Proxy file not found: {proxy_file}, running without proxies")
                return
            
            with open(proxy_file, "r") as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                line = line.strip()
                if line and not line.startswith("#"):
                    # Format: ip:port or ip:port:user:pass
                    self.proxies.append(line)
                    logger.debug(f"Loaded proxy {i}: {line}")
            
            logger.info(f"Loaded {len(self.proxies)} proxies")
        
        except Exception as e:
            logger.error(f"Error loading proxies: {str(e)}")
    
    def get_proxy(self, wallet_index):
        """Get proxy for wallet (round-robin)"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[wallet_index % len(self.proxies)]
        
        # Parse proxy format
        if "@" in proxy:
            # Format: user:pass@ip:port
            auth, host = proxy.split("@")
            user, password = auth.split(":")
            ip, port = host.split(":")
            return {
                "http": f"http://{user}:{password}@{ip}:{port}",
                "https": f"http://{user}:{password}@{ip}:{port}"
            }
        else:
            # Format: ip:port or ip:port:user:pass
            parts = proxy.split(":")
            if len(parts) == 2:
                ip, port = parts
                return {
                    "http": f"http://{ip}:{port}",
                    "https": f"http://{ip}:{port}"
                }
            elif len(parts) >= 4:
                ip, port, user, password = parts[0], parts[1], parts[2], parts[3]
                return {
                    "http": f"http://{user}:{password}@{ip}:{port}",
                    "https": f"http://{user}:{password}@{ip}:{port}"
                }
        
        return None
    
    def get_web3(self, wallet_index):
        """Get Web3 instance for wallet"""
        try:
            proxy = self.get_proxy(wallet_index)
            
            if proxy:
                logger.debug(f"Using proxy for wallet {wallet_index}")
                # Note: Web3.py doesn't directly support proxies via HTTPProvider
                # We'll use requests session with proxy for custom requests
                return Web3(Web3.HTTPProvider(self.rpc_url))
            else:
                return Web3(Web3.HTTPProvider(self.rpc_url))
        
        except Exception as e:
            logger.error(f"Error creating Web3 instance: {str(e)}")
            return None
    
    def get_account(self, wallet_index):
        """Get account for wallet"""
        if wallet_index < len(self.wallets):
            return self.wallets[wallet_index]["account"]
        return None
    
    def get_wallet_address(self, wallet_index):
        """Get wallet address"""
        if wallet_index < len(self.wallets):
            return self.wallets[wallet_index]["address"]
        return None
    
    def check_balance(self, wallet_index):
        """Check wallet balance"""
        try:
            w3 = self.get_web3(wallet_index)
            if not w3:
                return 0
            
            address = self.get_wallet_address(wallet_index)
            balance_wei = w3.eth.get_balance(address)
            balance_eth = Web3.from_wei(balance_wei, "ether")
            
            logger.debug(f"Wallet {wallet_index} balance: {balance_eth} ETH")
            return float(balance_eth)
        
        except Exception as e:
            logger.error(f"Error checking balance for wallet {wallet_index}: {str(e)}")
            return 0
    
    @property
    def wallet_count(self):
        """Get number of loaded wallets"""
        return len(self.wallets)

# Global wallet manager
wallet_manager = WalletManager()
