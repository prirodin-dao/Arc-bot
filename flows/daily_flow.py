"""
Daily automated flow — full AUTO‑ALL for ARC Testnet
"""

from modules.logger import logger
from modules.wallet import wallet_manager
from modules.faucet import faucet_handler
from modules.nft import nft_handler
from modules.deploy import deploy_handler
from modules.domains import domains_handler
from modules.gm import gm_handler
from flows.stats import stats
from modules.utils import delay
import random
import string


def random_string(length=6):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def run_daily_flow():
    logger.banner("🚀 DAILY AUTO‑ALL STARTED")

    total_wallets = wallet_manager.wallet_count
    logger.info(f"Loaded wallets: {total_wallets}")

    for wallet_index in range(total_wallets):
        logger.banner(f"🟦 Wallet {wallet_index + 1}/{total_wallets}")

        ok = True

        # 1) Faucet if needed
        logger.info("💧 Checking faucet...")
        faucet_ok = faucet_handler.claim_tokens(wallet_index)
        stats.record_operation("faucet", faucet_ok)
        if not faucet_ok:
            logger.warn("Faucet failed or skipped")

        # 2) Mint NFT
        logger.info("🖼 Minting NFT...")
        nft_ok = nft_handler.mint_nft(wallet_index, amount=1)
        stats.record_operation("nft", nft_ok)
        ok = ok and nft_ok

        # 3) Deploy token
        logger.info("🪙 Deploying token...")
        token_name = f"Token{random_string(4)}"
        token_symbol = f"T{random_string(3).upper()}"
        deploy_ok = deploy_handler.deploy_contract(wallet_index, token_name, token_symbol, 1_000_000)
        stats.record_operation("deploy", deploy_ok)
        ok = ok and deploy_ok

        # 4) Register domain
        logger.info("🌐 Registering domain...")
        domain = f"arc{random_string(6)}"
        domain_ok = domains_handler.register_domain(wallet_index, domain)
        stats.record_operation("domain", domain_ok)
        ok = ok and domain_ok

        # 5) Send GM
        logger.info("👋 Sending GM...")
        gm_ok = gm_handler.send_gm(wallet_index)
        stats.record_operation("gm", gm_ok)
        ok = ok and gm_ok

        # Record wallet result
        stats.record_wallet(ok)

        if ok:
            logger.success(f"✅ Wallet {wallet_index + 1} completed all operations")
        else:
            logger.error(f"❌ Wallet {wallet_index + 1} had errors")

        # Delay between wallets
        delay(3)

    logger.banner("🎉 DAILY AUTO‑ALL COMPLETED")
    stats.print_summary()
