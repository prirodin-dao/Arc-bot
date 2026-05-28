"""
Faucet module - получение тестовых токенов от Circle Faucet
"""
import requests
import asyncio
import aiohttp
from modules.logger import logger
from modules.wallet import wallet_manager
from config import CONTRACTS, BOT_CONFIG, TIMEOUTS
from modules.utils import get_retry_decorator, delay, rate_limiter

class FaucetHandler:
    """Handle Circle Faucet interactions"""
    
    def __init__(self):
        self.faucet_url = CONTRACTS["FAUCET_URL"]
        self.timeout = TIMEOUTS.get("faucet", 60)
    
    @get_retry_decorator(max_attempts=3)
    def claim_tokens(self, wallet_index):
        """Claim tokens from faucet for wallet"""
        try:
            wallet_address = wallet_manager.get_wallet_address(wallet_index)
            if not wallet_address:
                logger.error(f"Wallet {wallet_index} not found")
                return False
            
            logger.info(f"[Wallet {wallet_index}] Requesting tokens from faucet: {wallet_address}")
            
            # Circle Faucet requires manual interaction or API key
            # For now, we'll log the address and instructions
            logger.info(f"[Wallet {wallet_index}] Go to: {self.faucet_url}")
            logger.info(f"[Wallet {wallet_index}] Select: Arc Testnet")
            logger.info(f"[Wallet {wallet_index}] Enter address: {wallet_address}")
            logger.info(f"[Wallet {wallet_index}] Click: Send 10 USDC")
            
            rate_limiter.wait()
            return True
        
        except Exception as e:
            logger.error(f"Error claiming tokens from faucet: {str(e)}")
            return False
    
    async def async_claim_tokens(self, wallet_index):
        """Async claim tokens"""
        return self.claim_tokens(wallet_index)
    
    def get_faucet_instructions(self, wallet_index):
        """Get faucet instructions for user"""
        wallet_address = wallet_manager.get_wallet_address(wallet_index)
        if not wallet_address:
            return None
        
        instructions = f"""
╔════════════════════════════════════════════════════════════╗
║                   💧 FAUCET INSTRUCTIONS                    ║
╚════════════════════════════════════════════════════════════╝

Wallet #{wallet_index}
Address: {wallet_address}

Steps:
1. Go to: {self.faucet_url}
2. Select network: Arc Testnet
3. Paste address: {wallet_address}
4. Click "Send 10 USDC"
5. Wait for confirmation (~1 min)

Rate Limit: 1 request per hour per address
Amount: 10 USDC + native tokens

════════════════════════════════════════════════════════════
        """
        return instructions

# Global faucet handler
faucet_handler = FaucetHandler()
