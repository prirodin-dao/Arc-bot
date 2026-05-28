"""
Daily flow: прогон всех кошельков по всем операциям в нужном порядке
"""

import time

from config import BOT_CONFIG, FEATURES, OPERATION_ORDER
from modules.logger import logger
from modules.wallet import wallet_manager
from modules.faucet import faucet_handler
from modules.swaps import swap_handler
from modules.deploy import deploy_handler
from modules.domains import domains_handler
from modules.nft import nft_handler
from modules.gm import gm_handler


OPERATION_MAP = {
    "faucet": lambda idx: faucet_handler.claim_tokens(idx),
    "swaps": lambda idx: swap_handler.swap_tokens(idx),
    "deploy": lambda idx: deploy_handler.deploy_contract(idx),
    "domains": lambda idx: domains_handler.register_domain(idx),
    "nft": lambda idx: (
        nft_handler.create_nft(idx) and nft_handler.mint_nft(idx)
    ),
    "gm": lambda idx: gm_handler.send_gm(idx),
}


def run_operations_for_wallet(wallet_index: int):
    """Выполнить все включённые операции для одного кошелька"""
    address = wallet_manager.get_wallet_address(wallet_index)
    logger.banner(f"👛 Wallet #{wallet_index} | {address}")

    for op in OPERATION_ORDER:
        if not FEATURES.get(op.upper(), True):
            logger.info(f"[Wallet {wallet_index}] Skipping {op} (disabled in config)")
            continue

        handler = OPERATION_MAP.get(op)
        if not handler:
            logger.warning(f"[Wallet {wallet_index}] No handler for operation: {op}")
            continue

        logger.info(f"[Wallet {wallet_index}] ▶ Starting operation: {op}")
        try:
            ok = handler(wallet_index)
            if ok:
                logger.info(f"[Wallet {wallet_index}] ✅ Operation {op} completed")
            else:
                logger.warning(f"[Wallet {wallet_index}] ⚠ Operation {op} failed/was skipped")
        except Exception as e:
            logger.error(f"[Wallet {wallet_index}] ❌ Error in {op}: {e}")

        time.sleep(BOT_CONFIG["OPERATION_DELAY"])


def run_daily_flow():
    """Основной дневной цикл по всем кошелькам"""
    total = wallet_manager.wallet_count
    logger.info(f"Starting daily flow for {total} wallets")

    for idx in range(total):
        try:
            run_operations_for_wallet(idx)
        except Exception as e:
            logger.error(f"[Wallet {idx}] Fatal error, skipping wallet: {e}")

        # Пауза между кошельками
        time.sleep(BOT_CONFIG["WALLET_DELAY"])

    logger.info("Daily flow finished for all wallets")
