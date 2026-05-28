"""
Swaps module — ARC Testnet Router swaps (USDC <-> EURC + fallback StableSwap)
"""

from web3 import Web3
from modules.logger import logger
from modules.wallet import wallet_manager
from modules.utils import get_retry_decorator
from config import CONTRACTS, ABIS


ROUTER = Web3.to_checksum_address(CONTRACTS["ROUTER"])
POOL = Web3.to_checksum_address(CONTRACTS["POOL"])

USDC = Web3.to_checksum_address(CONTRACTS["USDC"])
EURC = Web3.to_checksum_address(CONTRACTS["EURC"])

ROUTER_ABI = ABIS["ROUTER"]
POOL_ABI = ABIS["POOL"]
ERC20_ABI = ABIS["ERC20"]


class SwapHandler:
    """Perform swaps on ARC Router + StableSwap fallback"""

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # INTERNAL: Approve
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # MAIN SWAP: USDC → EURC
    # ---------------------------------------------------------
    @get_retry_decorator(max_attempts=3)
    def swap_usdc_to_eurc(self, wallet_index, usdc_amount):
        """
        Swap USDC → EURC using Router.
        If Router fails (no pool), fallback to StableSwap Pool.
        """
        try:
            w3 = wallet_manager.get_web3(wallet_index)
            account = wallet_manager.get_account(wallet_index)
            address = wallet_manager.get_wallet_address(wallet_index)

            router = w3.eth.contract(address=ROUTER, abi=ROUTER_ABI)
            usdc = w3.eth.contract(address=USDC, abi=ERC20_ABI)

            logger.info(f"[Wallet {wallet_index}] Swapping {usdc_amount} USDC → EURC")

            # Convert amount to wei (USDC has 6 decimals)
            decimals = usdc.functions.decimals().call()
            amount_in = int(usdc_amount * (10 ** decimals))

            # Approve
            self._approve(w3, account, USDC, ROUTER, amount_in)

            # Try Router.getAmountsOut
            try:
                amounts = router.functions.getAmountsOut(
                    amount_in,
                    [USDC, EURC]
                ).call()
                expected_out = amounts[-1]
            except Exception as e:
                logger.warning(f"[Wallet {wallet_index}] Router path failed: {e}")
                return self._swap_stableswap_direct(wallet_index, amount_in)

            min_out = int(expected_out * 0.99)  # 1% slippage
            nonce = w3.eth.get_transaction_count(address)
            gas_price = w3.eth.gas_price

            tx = router.functions.swapExactTokensForTokens(
                amount_in,
                min_out,
                [USDC, EURC],
                address,
                w3.eth.get_block("latest").timestamp + 600
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

            logger.success(f"[Wallet {wallet_index}] Swap USDC→EURC OK (gas {receipt.gasUsed})")
            return True

        except Exception as e:
            logger.error(f"[Wallet {wallet_index}] Swap USDC→EURC failed: {e}")
            return False

    # ---------------------------------------------------------
    # FALLBACK: StableSwap Pool (Curve‑style)
    # ---------------------------------------------------------
    def _swap_stableswap_direct(self, wallet_index, amount_in):
        """
        Direct USDC <-> EURC swap via StableSwap Pool (exchange()).
        Pool index: 0 = USDC, 1 = EURC
        """
        try:
            w3 = wallet_manager.get_web3(wallet_index)
            account = wallet_manager.get_account(wallet_index)
            address = wallet_manager.get_wallet_address(wallet_index)

            pool = w3.eth.contract(address=POOL, abi=POOL_ABI)

            logger.info(f"[Wallet {wallet_index}] Fallback StableSwap: USDC→EURC")

            dy = pool.functions.get_dy(0, 1, amount_in).call()
            min_dy = int(dy * 0.99)

            nonce = w3.eth.get_transaction_count(address)
            gas_price = w3.eth.gas_price

            tx = pool.functions.exchange(
                0, 1, amount_in, min_dy
            ).build_transaction({
                "from": address,
                "nonce": nonce,
                "gasPrice": gas_price,
                "gas": 300_000,
                "chainId": w3.eth.chain_id,
            })

            signed = w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

            logger.info(f"[Wallet {wallet_index}] StableSwap TX: {tx_hash.hex()}")
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            logger.success(f"[Wallet {wallet_index}] StableSwap OK (gas {receipt.gasUsed})")
            return True

        except Exception as e:
            logger.error(f"[Wallet {wallet_index}] StableSwap failed: {e}")
            return False


swap_handler = SwapHandler()
