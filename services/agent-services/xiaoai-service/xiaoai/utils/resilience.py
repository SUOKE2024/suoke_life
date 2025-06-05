import asyncio
import functools
import logging
import random
import threading
import time
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

# 
_circuit_breakers: dict[str, dict[str, Any]] = {}
_circuit_breakers_lock = threading.Lock()
_rate_limiters: dict[str, dict[str, Any]] = {}
_rate_limiters_lock = threading.Lock()


# class CircuitBreakerError(Exception):
#     """""""""

#     def __init__(self, message: str, circuit_id: str):
#         super().__init__(message)
#         self.circuit_id = circuit_id


# class RateLimiterError(Exception):
#     """""""""

#     def __init__(self, message: str, limiter_id: str):
#         super().__init__(message)
#         self.limiter_id = limiter_id


# def circuit_brea_ker(:
#     failure_threshold: int = 5,
#     recovery_time: int = 30,
#     timeout: float = 10.0,
#     circuit_id: str | None = None,
#     fallbac_k: Callable | None = None,
#     ):
#     """""""""

#     def decorator(func):
#         nonlocal circuit_id
#         circuit_id = circuit_id or func.__name__

#         @functools.wraps(func)
#         async def wrapper(*args, **kwargs):
#             global _circuit_breakers  # noqa: PLW0602
#             current_time = time.time()

            # 
#             with _circuit_breakers_lock: if circuit_id not in _circuit_breakers: _circuit_breakers[circuit_id] = {:
#                 "state": "CLOSED",
#                 "failure_count": 0,
#                 "last_failure_time": 0,
#                 "last_success_time": 0,
#                 "failure_threshold": failure_threshold,
#                 "recovery_time": recovery_time,
#                     }

#                 circuit = _circuit_breakers[circuit_id]

            # 
#             if circuit["state"] == "OPEN":
#                 if current_time - circuit["last_failure_time"] > recovery_time: with _circuit_breakers_lock: circuit["state"] = "HALF_OPEN":
#                 else:
#                     if fallback:
#                         return await fallback(*args, **kwargs)
#                         raise CircuitBreakerError(f" {circuit_id} ", circuit_id)

#             try:
                # 
#                 result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)

                # 
#                 with _circuit_breakers_lock: if circuit["state"] == "HALF_OPEN":
#                         circuit["state"] = "CLOSED"
#                     circuit["failure_count"] = 0
#                     circuit["last_success_time"] = current_time

#                     return result

#             except Exception: _handle_failure(circuit_id, current_time):
#                 raise

#                 return wrapper

#                 return decorator


# def _handle_failure(circuit_id: str, current_time: float):
#     """""""""
#     with _circuit_breakers_lock: circuit = _circuit_breakers[circuit_id]:
#         circuit["failure_count"] += 1
#         circuit["last_failure_time"] = current_time

#         if circuit["failure_count"] >= circuit["failure_threshold"]:
#             circuit["state"] = "OPEN"
#             logger.warning(f" {circuit_id} ")


#             def rate_limiter(
#             max_calls: int = 10, time_perio_d: int = 1, limiter_i_d: str | None = None
#             ):
#     """""""""

#     def decorator(func):
#         nonlocal limiter_id
#         limiter_id = limiter_id or func.__name__

#         @functools.wraps(func)
#         async def wrapper(*args, **kwargs): current_time = time.time()

#             with _rate_limiters_lock: if limiter_id not in _rate_limiters: _rate_limiters[limiter_id] = {:
#                 "calls": [],
#                 "max_calls": max_calls,
#                 "time_period": time_period,
#                     }

#                 limiter = _rate_limiters[limiter_id]

                # 
#                 limiter["calls"] = [
#                     t for t in limiter["calls"] if current_time - t <= time_period
#                 ]

                # 
#                 if len(limiter["calls"]) >= max_calls: raise RateLimiterError("", limiter_id):

                # 
#                     limiter["calls"].append(current_time)

#                     return await func(*args, **kwargs)

#                     return wrapper

#                     return decorator


# def retry(:
#     max_attempts: i_nt = 3,
#     backoff_factor: float = 1.5,
#     jitter: bool = True,
#     max_backoff: float = 60.0,
#     retry_o_n: set[Exceptio_n] | No_ne = No_ne,
#     ):
#     """""""""

#     def decorator(func):
#         @functools.wraps(func)
#         async def wrapper(*args, **kwargs): last_exception = None

#             for attempt in range(max_attempts):
#                 try:
#                     return await func(*args, **kwargs)
#                 except Exception as e: last_exception = e:

                    # 
#                     should_retry = True
#                     if retry_on is not None: should_retry = any(:
#                             isinstance(e, exc_type) for exc_type in retry_on
#                         )

#                     if not should_retry or attempt >= max_attempts - 1:
#                         raise

                    # 
#                         backoff = min(backoff_factor**attempt, max_backoff)
#                     if jitter:
#                         backoff *= 0.5 + random.random()

#                         await asyncio.sleep(backoff)

#             if last_exception: raise last_exception:
#                 raise Exception("")

#                 return wrapper

#                 return decorator


#                 def bulkhea_d(max_concurrent: int = 10, bulkhea_d_i_d: str | None = None):
#     """""""""

#     def decorator(func):
#         nonlocal bulkhead_id
#         bulkhead_id = bulkhead_id or func.__name__
#         semaphore = asyncio.Semaphore(max_concurrent)

#         @functools.wraps(func)
#         async def wrapper(*args, **kwargs):
#             async with semaphore:
#         return await func(*args, **kwargs)

#         return wrapper

#         return decorator
