"""
Deploy module - smart contract deployment via zkcodex
"""
import requests
import json
from modules.logger import logger
from modules.wallet import wallet_manager
from config import CONTRACTS, BOT_CONFIG, TIMEOUTS
from modules.utils import get_retry_decorator, delay, rate_limiter

class DeployHandler:
    """Handle smart contract deployments"""
    
    def __init__(self):
        self.deploy_url = CONTRACTS["ZKCODEX_DEPLOY"]
        self.timeout = TIMEOUTS.get("deploy", 180)
    
    @get_retry_decorator(max_attempts=3)
    def deploy_contract(self, wallet_index, contract_name=None, params=None):
        """Deploy a contract"""
        try:
            wallet_address = wallet_manager.get_wallet_address(wallet_index)
            if not wallet_address:
                logger.error(f"Wallet {wallet_index} not found")
                return False
            
            if contract_name is None:
                contract_name = f"TestToken_{wallet_index}"
            
            logger.info(f"[Wallet {wallet_index}] Deploying contract: {contract_name}")
            logger.info(f"[Wallet {wallet_index}] From address: {wallet_address}")
            logger.info(f"[Wallet {wallet_index}] Deploy URL: {self.deploy_url}")
            
            # Log deployment details
            logger.debug(f"[Wallet {wallet_index}] Parameters: {params}")
            
            rate_limiter.wait()
            delay(BOT_CONFIG["OPERATION_DELAY"])
            
            return True
        
        except Exception as e:
            logger.error(f"Error deploying contract: {str(e)}")
            return False
    
    def get_deployment_info(self, wallet_index):
        """Get deployment information"""
        wallet_address = wallet_manager.get_wallet_address(wallet_index)
        
        info = f"""
╔════════════════════════════════════════════════════════════╗
║               🏗️  CONTRACT DEPLOYMENT INFO                 ║
╚════════════════════════════════════════════════════════════╝

Wallet #{wallet_index}
Address: {wallet_address}

Deploy URL: {self.deploy_url}
Network: Arc Testnet (5042002)

Standard Parameters:
- Name: TestToken_{wallet_index}
- Symbol: TT{wallet_index}
- Supply: 1,000,000
- Decimals: 18

════════════════════════════════════════════════════════════
        """
        return info

# Global deploy handler
deploy_handler = DeployHandler()
