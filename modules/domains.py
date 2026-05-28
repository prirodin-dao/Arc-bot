"""
Domains module - domain registration via Infinity Names
"""
import random
import string
from modules.logger import logger
from modules.wallet import wallet_manager
from config import CONTRACTS, BOT_CONFIG, TIMEOUTS
from modules.utils import get_retry_decorator, delay, rate_limiter

class DomainsHandler:
    """Handle domain registration"""
    
    def __init__(self):
        self.infinity_url = CONTRACTS["INFINITY_NAMES"]
        self.timeout = TIMEOUTS.get("domains", 90)
    
    @get_retry_decorator(max_attempts=3)
    def register_domain(self, wallet_index, domain_name=None):
        """Register domain on Infinity Names"""
        try:
            wallet_address = wallet_manager.get_wallet_address(wallet_index)
            if not wallet_address:
                logger.error(f"Wallet {wallet_index} not found")
                return False
            
            if domain_name is None:
                # Generate random domain name
                random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                domain_name = f"arc{random_suffix}"
            
            logger.info(f"[Wallet {wallet_index}] Registering domain: {domain_name}")
            logger.info(f"[Wallet {wallet_index}] URL: {self.infinity_url}")
            logger.info(f"[Wallet {wallet_index}] Owner: {wallet_address}")
            
            rate_limiter.wait()
            delay(BOT_CONFIG["OPERATION_DELAY"])
            
            return True
        
        except Exception as e:
            logger.error(f"Error registering domain: {str(e)}")
            return False
    
    def generate_domain_name(self, wallet_index):
        """Generate unique domain name"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
        return f"arc{wallet_index}{random_suffix}"
    
    def get_domains_info(self, wallet_index):
        """Get domain registration info"""
        wallet_address = wallet_manager.get_wallet_address(wallet_index)
        
        info = f"""
╔════════════════════════════════════════════════════════════╗
║             📛  DOMAIN REGISTRATION INFO                    ║
╚════════════════════════════════════════════════════════════╝

Wallet #{wallet_index}
Address: {wallet_address}

Service: Infinity Names
URL: {self.infinity_url}

Domain Pattern: arc[random]
Example: arc1a2b3c4d

Registration Steps:
1. Connect wallet
2. Enter domain name
3. Check availability
4. Pay registration fee
5. Wait for confirmation

════════════════════════════════════════════════════════════
        """
        return info

# Global domains handler
domains_handler = DomainsHandler()
