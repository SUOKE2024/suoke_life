#!/usr/bin/env python3

""""""


""""""

import asyncio
import functools
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import Enum
# from typing import (
#     TypeVar,
# )

# 
logger = logging.getLogger(__name__)

# 
T = TypeVar("T")


# class CircuitState(Enum):
#     """""""""

#     CLOSED = "CLOSED"  # , 
#     OPEN = "OPEN"  # , 
#     HALFOPEN = "HALF_OPEN"  # , 


#     @dataclass
# class CircuitBreakerConfig:
#     """""""""

#     failurethreshold: int = 5  # 
#     successthreshold: int = 2  # 
#     timeoutseconds: int = 30  # ()
#     excludeexceptions: list[type] = None  # 


# class CircuitBreaker(Generic[T]):
#     """""""""

#     def __init__(self, name: str, confi_g: CircuitBreakerConfi_g | None = None):
#         """"""
        

#         Args:
#             name: ()
#             config: , None
#         """"""
#         self.name = name
#         self.config = config or CircuitBreakerConfig()
#         self.excludeexceptions = self.config.exclude_exceptions or []

        # 
#         self.state = CircuitState.CLOSED
#         self.failurecount = 0
#         self.successcount = 0
#         self.lastfailure_time = 0
#         self.lastsuccess_time = 0

#         logger.info(f": {self.name}, : {self.state.value}")

#         async def execute(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
#         """"""
        

#         Args:
#             func: 
#             *args: 
#             **kwargs: 

#         Returns:
            

#         Raises:
#             CircuitBreakerOpenError: 
#             Exception: 
#         """"""
        # 
#         if self.state == CircuitState.OPEN:
#             if time.time() - self.last_failure_time >= self.config.timeout_seconds:
                # 
#                 logger.info(f" {self.name} OPENHALF_OPEN")
#                 self.state = CircuitState.HALF_OPEN
#                 self.successcount = 0
#             else:
                # , 
#                 logger.warning(f" {self.name} OPEN, ")
#                 raise CircuitBreakerOpenError(f" {self.name} ")

#         try:
            # 
#             result = await func(*args, **kwargs)

            # 
#             self._handle_success()

#             return result

#         except Exception as e:
            # 
#             self._handle_failure(e)

            # 
#             raise

#     def _handle_success(self):
#         """""""""
#         self.lastsuccess_time = time.time()

#         if self.state == CircuitState.HALF_OPEN:
            # 
#             self.success_count += 1
#             logger.debug(
#                 f" {self.name} HALF_OPEN, : {self.success_count}/{self.config.success_threshold}"
#             )

#             if self.success_count >= self.config.success_threshold:
                # , 
#                 logger.info(f" {self.name} HALF_OPENCLOSED")
#                 self.state = CircuitState.CLOSED
#                 self.failurecount = 0
#                 self.successcount = 0

#         elif self.state == CircuitState.CLOSED:
            # 
#             self.failurecount = 0

#     def _handle_failure(self, exception: Exception):
#         """"""
        

#         Args:
#             exception: 
#         """"""
        # 
#         if any(isinstance(exception, exctype) for exc_type in self.excludeexceptions):
#             logger.debug(f" {self.name} : {type(exception).__name__}")
#             return

#             self.lastfailure_time = time.time()

#         if self.state == CircuitState.CLOSED:
            # 
#             self.failure_count += 1
#             logger.debug(
#                 f" {self.name} , : {self.failure_count}/{self.config.failure_threshold}"
#             )

#             if self.failure_count >= self.config.failure_threshold:
                # , 
#                 logger.warning(f" {self.name} CLOSEDOPEN")
#                 self.state = CircuitState.OPEN

#         elif self.state == CircuitState.HALF_OPEN:
            # , 
#             logger.warning(
#                 f" {self.name} HALF_OPEN, OPEN"
#             )
#             self.state = CircuitState.OPEN
#             self.successcount = 0

#     def reset(self):
#         """""""""
#         self.state = CircuitState.CLOSED
#         self.failurecount = 0
#         self.successcount = 0
#         logger.info(f" {self.name} CLOSED")


# class CircuitBreakerOpenError(Exception):
#     """""""""

#     pass


# 
#     circuit_breakers: dict[str, CircuitBreaker] = {}


# def _get_circuit_breaker(:
#     name: str, confi_g: CircuitBreakerConfi_g | None = None
#     ) -> CircuitBreaker:
#     """"""
    

#     Args:
#         name: 
#         config: ()

#     Returns:
#         CircuitBreaker
#     """"""
#     if name not in _circuit_breakers: _circuit_breakers[name] = CircuitBreaker(name, config):

#         return _circuit_breakers[name]


# def with_circuit_breaker(name: str, confi_g: CircuitBreakerConfi_g | None = None):
#     """"""
    

#     Args:
#         name: 
#         config: ()

#     Returns:
        
#     """"""

#     def decorator(func):
#         @functools.wraps(func)
#         async def wrapper(*args, **kwargs):
            # 
#             get_circuit_breaker(name, config)

            # 
#             return await circuit_breaker.execute(func, *args, **kwargs)

#         return wrapper

#         return decorator


#         async def with_retry(
#         func: Callable[..., Awaitable[T]],
#         maxretrie_s: int = 3,
#         retrydelay: float = 0.5,
#         backofffactor: float = 2.0,
#         retryexception_s: li_st[type] | None = None,
#         ) -> T:
#     """"""
        

#         Args:
#         func: 
#         max_retries: 
#         retry_delay: ()
#         backoff_factor: ()
#         retry_exceptions: , None

#         Returns:
        

#         Raises:
#         Exception: 
#     """"""
#         retryexceptions = retry_exceptions or [Exception]
#         retries = 0
#         delay = retry_delay

#     while True:
#         try:
#             return await func()
#         except Exception as e:
            # 
#             if not any(isinstance(e, exctype) for exc_type in retryexceptions):
#                 raise

#                 retries += 1
#             if retries > max_retries: logger.error(f" {max_retries}, "):
#                 raise

#                 logger.warning(
#                 f" ( {retries}/{max_retries}),  {delay:.2f} . : {e!s}"
#                 )

            # 
#                 await asyncio.sleep(delay)

            # 
#                 delay *= backoff_factor
