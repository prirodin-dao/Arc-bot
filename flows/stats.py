"""
Statistics module for Arc Bot
"""

from modules.logger import logger

class Stats:
    def __init__(self):
        self.reset()

    def reset(self):
        self.total_wallets = 0
        self.success = 0
        self.failed = 0
        self.operations = {}

    def record_wallet(self, ok: bool):
        self.total_wallets += 1
        if ok:
            self.success += 1
        else:
            self.failed += 1

    def record_operation(self, op_name: str, ok: bool):
        if op_name not in self.operations:
            self.operations[op_name] = {"success": 0, "failed": 0}

        if ok:
            self.operations[op_name]["success"] += 1
        else:
            self.operations[op_name]["failed"] += 1

    def print_summary(self):
        logger.banner("📊 DAILY SUMMARY")

        logger.info(f"Wallets processed: {self.total_wallets}")
        logger.info(f"Successful: {self.success}")
        logger.info(f"Failed: {self.failed}")

        logger.info("Operations breakdown:")
        for op, data in self.operations.items():
            logger.info(f"  {op}: {data['success']} success / {data['failed']} failed")


stats = Stats()
