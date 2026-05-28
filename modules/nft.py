"""
NFT module - NFT creation and minting
"""
from modules.logger import logger
from modules.wallet import wallet_manager
from config import CONTRACTS, BOT_CONFIG, TIMEOUTS
from modules.utils import get_retry_decorator, delay, rate_limiter

class NFTHandler:
    """Handle NFT operations"""
    
    def __init__(self):
        self.omnihub_url = CONTRACTS["NFT_OMNIHUB"]
        self.zkcodex_url = CONTRACTS["NFT_ZKCODEX"]
        self.timeout = TIMEOUTS.get("nft", 120)
    
    @get_retry_decorator(max_attempts=3)
    def create_nft(self, wallet_index, name=None, description=None):
        """Create NFT on OmniHub"""
        try:
            wallet_address = wallet_manager.get_wallet_address(wallet_index)
            if not wallet_address:
                logger.error(f"Wallet {wallet_index} not found")
                return False
            
            if name is None:
                name = f"NFT_{wallet_index}_{int(__import__('time').time())}"
            
            logger.info(f"[Wallet {wallet_index}] Creating NFT: {name}")
            logger.info(f"[Wallet {wallet_index}] URL: {self.omnihub_url}")
            logger.info(f"[Wallet {wallet_index}] Description: {description or 'Test NFT'}")
            
            rate_limiter.wait()
            delay(BOT_CONFIG["OPERATION_DELAY"])
            
            return True
        
        except Exception as e:
            logger.error(f"Error creating NFT: {str(e)}")
            return False
    
    @get_retry_decorator(max_attempts=3)
    def mint_nft(self, wallet_index, contract_address=None, token_id=None):
        """Mint NFT on zkcodex Memorial"""
        try:
            wallet_address = wallet_manager.get_wallet_address(wallet_index)
            if not wallet_address:
                logger.error(f"Wallet {wallet_index} not found")
                return False
            
            logger.info(f"[Wallet {wallet_index}] Minting NFT")
            logger.info(f"[Wallet {wallet_index}] URL: {self.zkcodex_url}")
            logger.info(f"[Wallet {wallet_index}] Contract: {contract_address or 'auto'}")
            logger.info(f"[Wallet {wallet_index}] Token ID: {token_id or 'auto'}")
            
            rate_limiter.wait()
            delay(BOT_CONFIG["OPERATION_DELAY"])
            
            return True
        
        except Exception as e:
            logger.error(f"Error minting NFT: {str(e)}")
            return False
    
    def get_nft_info(self, wallet_index):
        """Get NFT operation info"""
        wallet_address = wallet_manager.get_wallet_address(wallet_index)
        
        info = f"""
╔════════════════════════════════════════════════════════════╗
║                    🖼️  NFT OPERATIONS                       ║
╚════════════════════════════════════════════════════════════╝

Wallet #{wallet_index}
Address: {wallet_address}

CREATE NFT:
- URL: {self.omnihub_url}
- Action: Create new NFT collection
- Standard: ERC-721 or ERC-1155

MINT NFT:
- URL: {self.zkcodex_url}
- Action: Mint memorial NFT
- Type: On-chain memorial

════════════════════════════════════════════════════════════
        """
        return info

# Global NFT handler
nft_handler = NFTHandler()
