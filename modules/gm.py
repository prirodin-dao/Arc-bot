"""
GM module - send daily GM messages on OnchainGM
"""
from datetime import datetime
from modules.logger import logger
from modules.wallet import wallet_manager
from config import CONTRACTS, BOT_CONFIG, TIMEOUTS
from modules.utils import get_retry_decorator, delay, rate_limiter

class GMHandler:
    """Handle OnchainGM messages"""
    
    def __init__(self):
        self.gm_url = CONTRACTS["ONCHAIN_GM"]
        self.timeout = TIMEOUTS.get("gm", 45)
    
    @get_retry_decorator(max_attempts=2)
    def send_gm(self, wallet_index, message=None):
        """Send GM message on-chain"""
        try:
            wallet_address = wallet_manager.get_wallet_address(wallet_index)
            if not wallet_address:
                logger.error(f"Wallet {wallet_index} not found")
                return False
            
            if message is None:
                message = f"GM from wallet {wallet_index} 🌅"
            
            logger.info(f"[Wallet {wallet_index}] Sending GM message")
            logger.info(f"[Wallet {wallet_index}] URL: {self.gm_url}")
            logger.info(f"[Wallet {wallet_index}] Message: {message}")
            logger.info(f"[Wallet {wallet_index}] Timestamp: {datetime.utcnow().isoformat()}")
            
            rate_limiter.wait()
            delay(BOT_CONFIG["OPERATION_DELAY"])
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending GM: {str(e)}")
            return False
    
    def get_gm_message(self, wallet_index):
        """Get default GM message"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        return f"GM from Arc Testnet Bot - Wallet {wallet_index} - {timestamp} ☀️"
    
    def get_gm_info(self, wallet_index):
        """Get GM operation info"""
        wallet_address = wallet_manager.get_wallet_address(wallet_index)
        
        info = f"""
╔════════════════════════════════════════════════════════════╗
║                  👋  ONCHAIN GM INFO                        ║
╚════════════════════════════════════════════════════════════╝

Wallet #{wallet_index}
Address: {wallet_address}

Service: OnchainGM
URL: {self.gm_url}

Operation:
- Type: Send on-chain message
- Frequency: Once per day
- Time: {datetime.utcnow().strftime("%H:%M UTC")}

Message Format:
GM from Arc Testnet Bot
Wallet: {wallet_address}
Timestamp: Auto-generated

════════════════════════════════════════════════════════════
        """
        return info

# Global GM handler
gm_handler = GMHandler()
