#!/usr/bin/env python3
""""""
# HTTP API
RESTful, 
""""""

import argparse
import asyncio
import logging
import os
import signal
import sys

# 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(_file__), "../..")))

# FastAPI
import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

# 
from internal.agent.agent_manager import AgentManager

from ..utils.config_manager import get_config_manager
from ..utils.metrics import get_metrics_collector

# 
logger = logging.getLogger(__name__)


# 
# class AppState:
#     """""""""

#     def __init__(self):
#         self.agentmanager: AgentManager | None = None
#         self.isshutting_down: bool = False
#         self.startuptime: float = 0.0

#         async def initialize(self):
#         """""""""
#         import time

#         time.time()

#         try:
            # 
#             self.agentmanager = AgentManager()
#             await self.agent_manager.initialize()

#             self.startuptime = time.time() - start_time
#             logger.info(f", : {self.startup_time:.2f}")

#         except Exception as e:
#             logger.error(f": {e}")
#             raise

#             async def cleanup(self):
#         """""""""
#             self.isshutting_down = True

#         if self.agent_manager: try:
#                 await self.agent_manager.close()
#                 logger.info("")
#             except Exception as e:
#                 logger.error(f": {e}")


# 
#                 appstate = AppState()


# def create_app() -> FastAPI:
#     """FastAPI""""""
    # 
#     config = get_config_manager()
#     config.get_section("http_server", {})

    # FastAPI
#     app = FastAPI(
#         title="",
#         description="",
#         version="1.0.0",
#         docs_url ="/docs",
#         redoc_url ="/redoc",
#         openapi_url ="/openapi.json",
#     )

    # 
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins =app_config.get("cors_origins", ["*"]),
#         allow_credentials =True,
#         allow_methods =["*"],
#         allow_headers =["*"],
#     )

#     app.add_middleware(GZipMiddleware, minimum_size =1000)

#     return app


#     async def get_agent_manager() -> AgentManager:
#     """""""""
#     if app_state.agent_manager is None:
#         raise HTTPException(status_code =503, detail="")

#     if app_state.is_shutting_down: raise HTTPException(status_code =503, detail=""):

#         return app_state.agent_manager


# def setup_routes(app: FastAPI):
#     """""""""

#     from internal.delivery.api.chat_handler import create_chat_router
#     from internal.delivery.api.device_handler import create_device_router
#     from internal.delivery.api.health_handler import create_health_router
#     from internal.delivery.api.network_handler import create_network_router

    # , 
#     app.include_router(create_device_router(getagent_manager))
#     app.include_router(create_chat_router(getagent_manager))
#     app.include_router(create_health_router(getagent_manager))
#     app.include_router(create_network_router(getagent_manager))

    # 
#     @app.get("/")
#     async def root():
#         """""""""
#         return {
#     "service": "",
#     "version": "1.0.0",
#     "status": "",
#     "startup_time": f"{app_state.startup_time:.2f}s",
#     "features": [
#     "",
#     "()",
#     "",
#     "",
#     "",
#     "",
#     ],
#         }

#     @app.get("/api/v1/status")
#     async def get_service_status(agentmgr: AgentManager = Depends(getagent_manager)):
#         """""""""
#         try:
            # 
#             devicestatus = await agent_mgr.get_device_status()

            # 
#             metrics = get_metrics_collector()

#             return JSONResponse(
#                 content={
#             "success": True,
#             "data": {
#             "service": "xiaoai-service",
#             "status": "healthy",
#             "startup_time": f"{app_state.startup_time:.2f}s",
#             "devices": devicestatus,
#             "active_sessions": len(agent_mgr.activesessions),
#             "metrics": {
#             "total_requests": metrics.get_total_requests(),
#             "active_connections": metrics.get_active_connections(),
#             },
#             },
#                 }
#             )

#         except Exception as e:
#             logger.error(f": {e}")
#             raise HTTPException(
#                 status_code =500, detail=f": {e!s}"
#             ) from e


# def handle_shutdown_signal(signum, frame):
#     """""""""
#     if app_state.is_shutting_down: logger.warning(", "):
#         return

#         signal.Signals(signum).name
#         logger.info(f" {signal_name}, ...")

    # 
#         asyncio.create_task(app_state.cleanup())


#         async def main():
#     """""""""
#         parser = argparse.ArgumentParser(description="HTTP API")
#         parser.add_argument("--config-dir", help="")
#         parser.add_argument("--env", help=" (development, staging, production)")
#         parser.add_argument("--host", default="0.0.0.0", help="")
#         parser.add_argument("--port", type=int, default=8000, help="")
#         args = parser.parse_args()

    # 
#     if args.config_dir: os.environ["XIAOAI_CONFIG_DIR"] = args.config_dir:
#     if args.env:
#         os.environ["ENV"] = args.env

    # 
#         config = get_config_manager()

    # 
#         logging.basicConfig(
#         level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
#         )

    # 
#         signal.signal(signal.SIGINT, handleshutdown_signal)
#         signal.signal(signal.SIGTERM, handleshutdown_signal)

#     try:
        # 
#         await app_state.initialize()

        # 
#         app = create_app()

        # 
#         setup_routes(app)

        # 
#         config.get_section("http_server", {})
#         host = args.host or http_config.get("host", "0.0.0.0")
#         port = args.port or http_config.get("port", 8000)

#         logger.info(f"HTTP API, : {host}:{port}")

        # 
#         configuvicorn = uvicorn.Config(
#             app, host=host, port=port, log_level ="info", access_log =True, loop="asyncio"
#         )

#         server = uvicorn.Server(configuvicorn)
#         await server.serve()

#     except Exception as e:
#         logger.error(f"HTTP: {e!s}", exc_info =True)
#         sys.exit(1)

#     finally:
        # 
#         await app_state.cleanup()


# if __name__ == "__main__":
    # 
#     asyncio.run(main())
