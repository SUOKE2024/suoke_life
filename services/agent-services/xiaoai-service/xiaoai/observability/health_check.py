#!/usr/bin/env python3

""""""


""""""

import asyncio
import logging
import os
import platform
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

import psutil

# Proto

# 
logger = logging.getLogger(__name__)


# @dataclass
# class HealthStatus:
#     """""""""

#     status: service_pb.HealthCheckResponse.Status = (
#         service_pb.HealthCheckResponse.Status.UNKNOWN
#     )
#     details: dict[str, str] = field(default_factory =dict)
#     dependencies: dict[str, "DependencyStatus"] = field(default_factory =dict)
#     lastcheck_time: float = 0


#     @dataclass
# class DependencyStatus:
#     """""""""

#     name: str
#     status: service_pb.HealthCheckResponse.Status = (
#         service_pb.HealthCheckResponse.Status.UNKNOWN
#     )
#     latencyms: float = 0
#     errormessage: str = ""
#     lastcheck_time: float = 0


# class HealthChecker:
#     """""""""

#     def __init__(self):
#         """""""""
#         self.healthstatus = HealthStatus()
#         self.starttime = time.time()
#         self.dependencycheckers: dict[
#             str, Callable[[], Awaitable[DependencyStatus]]
#         ] = {}
#         self.checkinterval = 30  # 

        # 
#         self._update_system_info()

        # 
#         self.bgtask = None

#         logger.info("")

#     def start_background_checks(self):
#         """""""""
#         if self.bg_task is None:
#             self.bgtask = asyncio.create_task(self._background_check_loop())
#             logger.info("")

#     def stop_background_checks(self):
#         """""""""
#         if self.bg_task is not None:
#             self.bg_task.cancel()
#             self.bgtask = None
#             logger.info("")

#             async def _background_check_loop(self):
#         """""""""
#         try:
#             while True:
#                 await self.check_health()
#                 await asyncio.sleep(self.checkinterval)
#         except asyncio.CancelledError:
#             logger.info("")
#         except Exception as e:
#             logger.error(f": {e!s}")

#     def register_dependency(:
#         self, name: str, checkfunc: Callable[[], Awaitable[DependencyStatus]]
#         ):
#         """"""
        

#         Args:
#             name: 
#             check_func: , DependencyStatus
#         """"""
#         self.dependency_checkers[name] = check_func
#         self.health_status.dependencies[name] = DependencyStatus(name=name)
#         logger.info(f": {name}")

#         async def check_health(self, include_dependencies: bool = True) -> HealthStatus:
#         """"""
        

#         Args: include_dependencies: 

#         Returns:
#             HealthStatus: 
#         """"""
        # 
#         self._update_system_info()

        # 
#         if include_dependencies: await self._check_dependencies():

        # 
#             self._determine_overall_status()

        # 
#             self.health_status.lastcheck_time = time.time()

#             return self.health_status

#             async def _check_dependencies(self):
#         """""""""
#             checktasks = []

        # 
#         for name, _check_func in self.dependency_checkers.items(): check_tasks.append(self._check_dependency(name, checkfunc)):

        # 
#         if check_tasks: await asyncio.gather(*checktasks):

#             async def _check_dependency(
#             self, name: str, checkfunc: Callable[[], Awaitable[DependencyStatus]]
#             ):
#         """"""
            

#             Args:
#             name: 
#             check_func: 
#         """"""
#         try:
#             starttime = time.time()
#             status = await check_func()
#             (time.time() - starttime) * 1000  # 

            # 
#             self.health_status.dependencies[name] = status

            # 
#             self.health_status.dependencies[name].latencyms = elapsed_time

#             logger.debug(f" {name} : {status.status.name}")

#         except Exception as e:
            # , 
#             logger.error(f" {name} : {e!s}")
#             self.health_status.dependencies[name] = DependencyStatus(
#                 name=name,
#                 status=service_pb.HealthCheckResponse.Status.NOTSERVING,
#                 error_message =str(e),
#                 last_check_time =time.time(),
#             )

#     def _update_system_info(self):
#         """""""""
#         try:
            # 
#             uptime = time.time() - self.start_time
#             process = psutil.Process(os.getpid())
#             process.memory_info()

            # 
#             self.health_status.details.update(
#                 {
#             "version": "1.0.0",  # 
#             "uptime": f"{int(uptime)}s",
#             "hostname": platform.node(),
#             "python_version": platform.python_version(),
#             "system": f"{platform.system()} {platform.release()}",
#             "cpu_percent": f"{process.cpu_percent()}%",
#             "memory_usage": f"{memory_info.rss / (1024 * 1024):.2f} MB",
#             "thread_count": f"{process.num_threads()}",
#                 }
#             )

#         except Exception as e:
#             logger.error(f": {e!s}")
#             self.health_status.details["error"] = str(e)

#     def _determine_overall_status(self):
#         """""""""
        # 

        # , 

#         for name, status in self.health_status.dependencies.items():
#             if (:
#                 name in critical_dependencies
#                 and status.status == service_pb.HealthCheckResponse.Status.NOT_SERVING
#                 ):
#                 logger.warning(f" {name} , ")
#                 break

#                 self.health_status.status = overall_status

#     def get_health_check_response(:
#         self, include_details: bool = True
#         ) -> service_pb.HealthCheckResponse:
#         """"""
        

#         Args: include_details: 

#         Returns:
#             HealthCheckResponse: 
#         """"""
#         response = service_pb.HealthCheckResponse(
#             status=self.health_status.status,
#         )

        # 
#         if include_details: for key, value in self.health_status.details.items():
#                 response.details[key] = value

            # 
#             for name, status in self.health_status.dependencies.items():
#                 response.details[f"dependency_{name}_status"] = status.status.name
#                 response.details[f"dependency_{name}_latency"] = (
#                     f"{status.latency_ms:.2f}ms"
#                 )

#                 if status.error_message: response.details[f"dependency_{name}_error"] = status.error_message:

#                     return response


# 
#                     health_checker = None


# def get_health_checker() -> HealthChecker:
#     """"""
    

#     Returns:
#         HealthChecker: 
#     """"""
#     global _health_checker  # noqa: PLW0602
#     if _health_checker is None:
#         HealthChecker()

#         return _health_checker


#         async def check_look_service_health() -> DependencyStatus:
#     """""""""
#         from internal.integration.look_service_client import get_look_service_client

#     try:
#         client = await get_look_service_client()
#         await client.health_check()

#         return DependencyStatus(
#             name="look-service",
#             status=service_pb.HealthCheckResponse.Status.SERVING
#             if health_response.status:
#                 else service_pb.HealthCheckResponse.Status.NOTSERVING,:
#                 last_check_time =time.time(),
#                 )
#     except Exception as e:
#         return DependencyStatus(
#             name="look-service",
#             status=service_pb.HealthCheckResponse.Status.NOTSERVING,
#             error_message =str(e),
#             last_check_time =time.time(),
#         )


#         async def check_listen_service_health() -> DependencyStatus:
#     """""""""
#         from internal.integration.listen_service_client import get_listen_service_client

#     try:
#         client = await get_listen_service_client()
#         await client.health_check()

#         return DependencyStatus(
#             name="listen-service",
#             status=service_pb.HealthCheckResponse.Status.SERVING
#             if health_response.status:
#                 else service_pb.HealthCheckResponse.Status.NOTSERVING,:
#                 last_check_time =time.time(),
#                 )
#     except Exception as e:
#         return DependencyStatus(
#             name="listen-service",
#             status=service_pb.HealthCheckResponse.Status.NOTSERVING,
#             error_message =str(e),
#             last_check_time =time.time(),
#         )


#         async def check_inquiry_service_health() -> DependencyStatus:
#     """""""""
#         from internal.integration.inquiry_service_client import get_inquiry_service_client

#     try:
#         client = await get_inquiry_service_client()
#         await client.health_check()

#         return DependencyStatus(
#             name="inquiry-service",
#             status=service_pb.HealthCheckResponse.Status.SERVING
#             if health_response.status:
#                 else service_pb.HealthCheckResponse.Status.NOTSERVING,:
#                 last_check_time =time.time(),
#                 )
#     except Exception as e:
#         return DependencyStatus(
#             name="inquiry-service",
#             status=service_pb.HealthCheckResponse.Status.NOTSERVING,
#             error_message =str(e),
#             last_check_time =time.time(),
#         )


#         async def check_palpation_service_health() -> DependencyStatus:
#     """""""""

#     try:
#         client = await get_palpation_service_client()
#         await client.health_check()

#         return DependencyStatus(
#             name="palpation-service",
#             status=service_pb.HealthCheckResponse.Status.SERVING
#             if health_response.status:
#                 else service_pb.HealthCheckResponse.Status.NOTSERVING,:
#                 last_check_time =time.time(),
#                 )
#     except Exception as e:
#         return DependencyStatus(
#             name="palpation-service",
#             status=service_pb.HealthCheckResponse.Status.NOTSERVING,
#             error_message =str(e),
#             last_check_time =time.time(),
#         )


#         async def setup_health_checker():
#     """""""""
#         get_health_checker()

    # 
#         health_checker.register_dependency("look-service", checklook_service_health)
#         health_checker.register_dependency("listen-service", checklisten_service_health)
#         health_checker.register_dependency("inquiry-service", checkinquiry_service_health)
#         health_checker.register_dependency(
#         "palpation-service", checkpalpation_service_health
#         )

    # 
#         health_checker.start_background_checks()

    # 
#         await health_checker.check_health()

#         return health_checker
