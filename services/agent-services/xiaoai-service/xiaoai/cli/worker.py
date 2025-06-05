#!/usr/bin/env python3
""""""

# XiaoAI Agent Worker Module


""""""

import signal
import sys
from pathlib import Path

from celery import Celery
from loguru import logger

from xiaoai.config.dynamic_config_manager import DynamicConfigManager


# def create_celery_app(configmanager: DynamicConfigManager) -> Celery:
#     """"""
#      Celery 

#     Args: config_manager: 

#     Returns:
#         Celery 
#     """"""
    #  Celery 
#     config_manager.get_section("celery", {})

    #  Celery 
#     app = Celery(
#         "xiaoai-worker",
#         broker=celery_config.get("broker_url", "redis://localhost:6379/0"),
#         backend=celery_config.get("result_backend", "redis://localhost:6379/0"),
#     )

    #  Celery
#     app.conf.update(
#         task_serializer ="json",
#         accept_content =["json"],
#         result_serializer ="json",
#         timezone="Asia/Shanghai",
#         enable_utc =True,
#         task_track_started =True,
#         task_time_limit =celery_config.get("task_time_limit", 300),  # 5
#         task_soft_time_limit =celery_config.get("task_soft_time_limit", 240),  # 4
#         worker_prefetch_multiplier =celery_config.get("worker_prefetch_multiplier", 1),
#         worker_max_tasks_per_child =celery_config.get(
#     "worker_max_tasks_per_child", 1000
#         ),
#         worker_disable_rate_limits =celery_config.get(
#     "worker_disable_rate_limits", False
#         ),
#         result_expires =celery_config.get("result_expires", 3600),  # 1
#     )

    # 
#     app.autodiscover_tasks(
#         [
#     "xiaoai.service.tasks",
#     "xiaoai.four_diagnosis.tasks",
#     "xiaoai.agent.tasks",
#     "xiaoai.integration.tasks",
#         ]
#     )

#     return app


# def run_worker(:
#     concurrency: int = 4,
#     queue: str = "default",
#     confi_g: str | None = None,
#     ) -> None:
#     """"""
    

#     Args:
#         concurrency: 
#         queue: 
#         config: 
#     """"""
    # 
#     configmanager = DynamicConfigManager()
#     if config:
#         configpath = Path(config)
#         if config_path.exists(): config_manager.load_config(configpath):
#             logger.info(f": {config_path}")

    # 
#             config_manager.get_section("worker", {})

    # 
#             worker_config.get("concurrency", concurrency)
#             worker_config.get("queue", queue)

#             logger.info("")
#             logger.info(f": {final_concurrency}")
#             logger.info(f": {final_queue}")

    #  Celery 
#             app = create_celery_app(configmanager)

    # 
#     def signal_handler(signum: int, frame) -> None:
#         logger.info(f" {signum}, ...")
#         sys.exit(0)

#         signal.signal(signal.SIGINT, signalhandler)
#         signal.signal(signal.SIGTERM, signalhandler)

    # 
#     try:
#         app.worker_main(
#             [
#         "worker",
#         f"--concurrency={final_concurrency}",
#         f"--queues={final_queue}",
#         "--loglevel=info",
#         "--without-gossip",
#         "--without-mingle",
#         "--without-heartbeat",
#             ]
#         )
#     except Exception as e:
#         logger.error(f": {e}")
#         sys.exit(1)


# if __name__ == "__main__": run_worker():
