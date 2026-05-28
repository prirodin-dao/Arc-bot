"""
Swaps module — ARC Testnet Router swaps (ETH <-> USDC)
"""

from web3 import Web3
from modules.logger import logger
from modules.wallet import wallet_manager
from modules.utils import get_retry_decorator
from config import CONTRACTS, ABIS

ROUTER = Web3.to_checksum_address(CONTRACTS["ROUTER"])
USDC = Web3.to_checksum_address(CONTRACTS["USDC"])

ROUTER_ABI = ABIS["ROUTER"]
ERC20_ABI = ABIS["ERC20"]


class SwapHandler:
    """Perform swaps on ARC Router"""

    def __init__(self):
        pass

    def _approve(self, w3, account, token, spender, amount):
        contract = w3.eth.contract(address=token, abi=ERC20_ABI)
        address = account.address

        nonce = w3.eth.get_transaction_count(address)
        gas_price = w3.eth.gas_price

        tx = contract.functions.approve(
            spender,
            amount
        ).build_transaction({
            "from": address,
            "nonce": nonce,
            "gasPrice": gas_price,
            "gas": 200_000,
            "chainId": w3.eth.chain_id,
        })

        signed = w3.eth.account.sign_transaction(tx, account.key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

        logger.info(f"[{address[:6]}] Approve TX: {tx_hash.hex()}")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        logger.success(f"[{address[:6]}] Approve OK (gas {receipt.gasUsed})")

    @get_retry_decorator(max_attempts=3)
    def swap_eth_to_usdc(self, wallet_index, eth_amount):
        """Swap ETH → USDC"""
        try:
            w3 = wallet_manager.get_web3(wallet_index)
            account = wallet_manager.get_account(wallet_index)
            address = wallet_manager.get_wallet_address(wallet_index)

            router = w3.eth.contract(address=ROUTER, abi=ROUTER_ABI)

            logger.info(f"[Wallet {wallet_index}] Swapping {eth_amount} ETH → USDC")

            nonce = w3.eth.get_transaction_count(address)
            gas_price = w3.eth.gas_price

            tx = router.functions.swapExactETHForTokens(
                0,  # minOut
                [w3.to_checksum_address(CONTRACTS["WETH"]), USDC],
                address
            ).build_transaction({
                "from": address,
                "nonce": nonce,
                "value": Web3.to_wei(eth_amount, "ether"),
                "gasPrice": gas_price,
                "gas": 500_000,
                "chainId": w3.eth.chain_id,
            })

            signed = w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

            logger.info(f"[Wallet {wallet_index}] Swap TX: {tx_hash.hex()}")
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            logger.success(f"[Wallet {wallet_index}] Swap ETH→USDC OK (gas {receipt.gasUsed})")
            return True

        except Exception as e:
            logger.error(f"[Wallet {wallet_index}] Swap ETH→USDC failed: {e}")
            return False

    @get_retry_decorator(max_attempts=3)
    def swap_usdc_to_eth(self, wallet_index, usdc_amount):
        """Swap USDC → ETH"""
        try:
            w3 = wallet_manager.get_web3(wallet_index)
            account = wallet_manager.get_account(wallet_index)
            address = wallet_manager.get_wallet_address(wallet_index)

            router = w3.eth.contract(address=ROUTER, abi=ROUTER_ABI)
            usdc = w3.eth.contract(address=USDC, abi=ERC20_ABI)

            logger.info(f"[Wallet {wallet_index}] Swapping {usdc_amount} USDC → ETH")

            # Approve
            self._approve(
                w3,
                account,
                USDC,
                ROUTER,
                Web3.to_wei(usdc_amount, "ether")
            )

            nonce = w3.eth.get_transaction_count(address)
            gas_price = w3.eth.gas_price

            tx = router.functions.swapExactTokensForETH(
                Web3.to_wei(usdc_amount, "ether"),
                0,  # minOut
                [USDC, w3.to_checksum_address(CONTRACTS["WETH"])],
                address
            ).build_transaction({
                "from": address,
                "nonce": nonce,
                "gasPrice": gas_price,
                "gas": 500_000,
                "chainId": w3.eth.chain_id,
            })

            signed = w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

            logger.info(f"[Wallet {wallet_index}] Swap TX: {tx_hash.hex()}")
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            logger.success(f"[Wallet {wallet_index}] Swap USDC→ETH OK (gas {receipt.gasUsed})")
            return True

        except Exception as e:
            logger.error(f"[Wallet {wallet_index}] Swap USDC→ETH failed: {e}")
            return False


swap_handler = SwapHandler()
