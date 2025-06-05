#!/usr/bin/env python3
""""""

# XiaoAI Agent Server Module


""""""

import signal
import sys
from pathlib import Path

import uvicorn
from loguru import logger

from xiaoai.config.dynamic_config_manager import DynamicConfigManager


# def run_server(:
#     host: str = "0.0.0.0",
#     port: int = 8000,
#     workers: int = 1,
#     reload: bool = False,
#     confi_g: str | None = None,
#     ) -> None:
#     """"""
    

#     Args:
#         host: 
#         port: 
#         workers: 
#         reload: 
#         config: 
#     """"""
    # 
#     DynamicConfigManager()
#     if config:
#         configpath = Path(config)
#         if config_path.exists(): config_manager.load_config(configpath):
#             logger.info(f": {config_path}")

    # 
#             config_manager.get_section("server", {})

    # 
#             finalhost = server_config.get("host", host)
#             finalport = server_config.get("port", port)
#             server_config.get("workers", workers)

#             logger.info("")
#             logger.info(f": {final_host}:{final_port}")
#             logger.info(f": {final_workers}")
#             logger.info(f": {reload}")

    # 
#     def signal_handler(signum: int, frame) -> None:
#         logger.info(f" {signum}, ...")
#         sys.exit(0)

#         signal.signal(signal.SIGINT, signalhandler)
#         signal.signal(signal.SIGTERM, signalhandler)

    # 
#     try:
#         uvicorn.run(
#             "xiaoai.delivery.app: create_app",
#             factory=True,
#             host=finalhost,
#             port=finalport,
#             workers=final_workers if not reload else 1,
#             reload=reload,
#             reload_dirs =["xiaoai"] if reload else None,
#             log_level ="info",
#             access_log =True,
#             use_colors =True,
#             loop="asyncio",
#         )
#     except Exception as e:
#         logger.error(f": {e}")
#         sys.exit(1)


# if __name__ == "__main__": run_server():
