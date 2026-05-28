"""
Daily automated flow — Optimized Multi-threaded Flow with Anti-Sybil protection
"""

import random
import string
import time
from concurrent.futures import ThreadPoolExecutor

from modules.logger import logger
from modules.wallet import wallet_manager
from modules.faucet import faucet_handler
from modules.nft import nft_handler
from modules.deploy import deploy_handler
from modules.domains import domains_handler
from modules.gm import gm_handler
from modules.swaps import swap_handler
from flows.stats import stats
from config import BOT_CONFIG


def random_string(length=6):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def process_single_wallet(wallet_index, total_wallets):
    """Логика выполнения задач для одного конкретного кошелька в отдельном потоке"""
    # Задержка на старте, чтобы кошельки не отправляли транзакции в одну секунду
    start_sleep = random.uniform(5, 120)
    logger.info(f"[Wallet {wallet_index + 1}] Пауза перед стартом {start_sleep:.1f} сек. для рандомизации времени...")
    time.sleep(start_sleep)

    logger.banner(f"🟦 Поток запущен: Кошелек {wallet_index + 1}/{total_wallets}")
    ok = True

    # Шаг 1: Проверка и получение токенов из крана (Всегда идет первым, чтобы был газ)
    logger.info(f"[Wallet {wallet_index + 1}] 💧 Проверка крана...")
    faucet_ok = faucet_handler.claim_tokens(wallet_index)
    stats.record_operation("faucet", faucet_ok)
    
    time.sleep(random.uniform(5, 15))

    # АНТИ-СИБИЛ ЗАЩИТА: Перемешиваем последовательность остальных действий!
    # У каждого кошелька будет своя уникальная история действий на блокчейне
    activities = ["nft", "deploy", "domain", "gm", "swap"]
    random.shuffle(activities)
    
    logger.info(f"[Wallet {wallet_index + 1}] Случайный порядок ончейн-шагов: {', '.join(activities)}")

    for activity in activities:
        try:
            if activity == "nft":
                logger.info(f"[Wallet {wallet_index + 1}] 🖼 Минт NFT...")
                nft_ok = nft_handler.mint_nft(wallet_index)
                stats.record_operation("nft", nft_ok)
                ok = ok and nft_ok

            elif activity == "deploy":
                logger.info(f"[Wallet {wallet_index + 1}] 📜 Деплой токена...")
                contract = deploy_handler.deploy_contract(wallet_index)
                deploy_ok = bool(contract)
                stats.record_operation("deploy", deploy_ok)
                ok = ok and deploy_ok

            elif activity == "domain":
                logger.info(f"[Wallet {wallet_index + 1}] 🌐 Регистрация домена...")
                domain = f"arc{random_string(6)}"
                domain_ok = domains_handler.register_domain(wallet_index, domain)
                stats.record_operation("domain", domain_ok)
                ok = ok and domain_ok

            elif activity == "gm":
                logger.info(f"[Wallet {wallet_index + 1}] 👋 Отправка транзакции GM...")
                gm_ok = gm_handler.send_gm(wallet_index)
                stats.record_operation("gm", gm_ok)
                ok = ok and gm_ok

            elif activity == "swap":
                usdc_amount = BOT_CONFIG["SWAP_USDC_AMOUNT"]
                logger.info(f"[Wallet {wallet_index + 1}] 💱 Свап {usdc_amount} USDC → EURC...")
                swap_ok = swap_handler.swap_usdc_to_eurc(wallet_index, usdc_amount)
                stats.record_operation("swap_usdc_to_eurc", swap_ok)
                ok = ok and swap_ok

        except Exception as e:
            logger.error(f"[Wallet {wallet_index + 1}] Непредвиденная ошибка на шаге {activity}: {e}")
            ok = False

        # Небольшая случайная пауза между действиями внутри одного кошелька
        time.sleep(random.uniform(10, 25))

    stats.record_wallet(ok)
    if ok:
        logger.success(f"✅ Кошелек {wallet_index + 1} успешно прошел весь круг!")
    else:
        logger.error(f"❌ Кошелек {wallet_index + 1} завершил работу с ошибками.")


def run_daily_flow():
    logger.banner("🚀 DAILY MULTI-THREADED FLOW STARTED")

    total_wallets = wallet_manager.wallet_count
    logger.info(f"Loaded wallets total: {total_wallets}")

    if total_wallets == 0:
        return

    # Задаем размер группы одновременных кошельков.
    # 3-4 кошелька одновременно — идеальный баланс, чтобы RPC нода не выдала ошибку "Too Many Requests"
    MAX_THREADS = min(4, total_wallets)
    logger.info(f"Запускается многопоточный пул. Одновременно работают кошельков: {MAX_THREADS}")

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # Отправляем все кошельки на параллельную обработку
        futures = [
            executor.submit(process_single_wallet, idx, total_wallets)
            for idx in range(total_wallets)
        ]
        
        # Ждем выполнения всех кошельков из списка
        for future in futures:
            future.result()

    logger.banner("🎉 DAILY MULTI-THREADED FLOW COMPLETED")
    stats.print_summary()
