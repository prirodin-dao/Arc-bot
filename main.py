import logging
from datetime import datetime, time as dtime

from apscheduler.schedulers.blocking import BlockingScheduler

from config import BOT_CONFIG, FEATURES
from modules.logger import logger
from modules.wallet import wallet_manager
from flows.daily_flow import run_daily_flow


def daily_job():
    """Основная дневная задача: прогон всех кошельков по всем операциям"""
    logger.banner("🚀 Starting daily Arc Testnet run")

    if wallet_manager.wallet_count == 0:
        logger.error("No wallets loaded. Check private.txt")
        return

    try:
        run_daily_flow()
        logger.banner("✅ Daily run finished")
    except Exception as e:
        logger.error(f"Fatal error in daily job: {e}")


def setup_scheduler():
    """Настройка ежедневного запуска по времени из конфигурации"""
    sched = BlockingScheduler(timezone="UTC")

    hh, mm = BOT_CONFIG["SCHEDULE_TIME"].split(":")
    run_time = dtime(hour=int(hh), minute=int(mm))

    logger.info(f"Scheduling daily job at {BOT_CONFIG['SCHEDULE_TIME']} UTC")

    sched.add_job(
        daily_job,
        trigger="cron",
        hour=run_time.hour,
        minute=run_time.minute,
        id="daily_arc_run",
        replace_existing=True,
    )

    try:
        logger.banner("🕒 Scheduler started, waiting for next run...")
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    logger.banner("🔥 Arc Testnet Bot starting up")

    logger.info(f"Loaded wallets: {wallet_manager.wallet_count}")
    logger.info(f"Enabled features: {', '.join([k for k, v in FEATURES.items() if v])}")

    # Один прогон сразу при старте
    daily_job()

    # А дальше — по расписанию
    setup_scheduler()
