#!/usr/bin/env python3
""""""

""""""

import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# @dataclass
# class MetricEntry:
#     """""""""

#     name: str
#     value: float
#     timestamp: float
#     tags: dict[str, str] = field(default_factory =dict)


# class MetricsCollector:
#     """""""""

#     def __init__(self, max_entries: int = 10000):
#         self.max_entries = max_entries
#         self.metrics: dict[str, deque] = defaultdict(lambda: deque(maxlen=max_entries))
#         self.counters: dict[str, float] = defaultdict(float)
#         self.gauges: dict[str, float] = defaultdict(float)
#         self.timers: dict[str, list[float]] = defaultdict(list)
#         self.lock = threading.RLock()

        # 
#         self.request_count = 0
#         self.error_count = 0
#         self.total_response_time = 0.0
#         self.start_time = time.time()

#     def increment_counter(:
#         _self, name: _str, value: float = 1.0, tag_s: Optional[Dict[_str, _str]] = None
#         ):
#         """""""""
#         with self.lock:
#             self.counters[name] += value
#             self._add_metric(name, value, tags or {})

#     def _set_gauge(_self, name: _str, value: float, tag_s: Optional[Dict[_str, _str]] = None):
#         """""""""
#         with self.lock:
#             self.gauges[name] = value
#             self._add_metric(name, value, tags or {})

#     def record_timer(:
#         _self, name: _str, duration: float, tag_s: Optional[Dict[_str, _str]] = None
#         ):
#         """""""""
#         with self.lock:
#             self.timers[name].append(duration)
            # 1000
#             if len(self.timers[name]) > 1000:
#                 self.timers[name] = self.timers[name][-1000:]
#                 self._add_metric(name, duration, tags or {})

#     def _add_metric(self, name: str, value: float, tags: dict[str, str]):
#         """""""""
#         entry = MetricEntry(name=name, value=value, timestamp=time.time(), tags=tags)
#         self.metrics[name].append(entry)

#     def get_counter(self, name: str) -> float:
#         """""""""
#         with self.lock:
#             return self.counters.get(name, 0.0)

#     def get_gauge(self, name: str) -> float:
#         """""""""
#         with self.lock:
#             return self.gauges.get(name, 0.0)

#     def get_timer_stats(self, name: str) -> dict[str, float]:
#         """""""""
#         with self.lock:
#             values = self.timers.get(name, [])
#             if not values:
#                 return {}

#                 sorted_values = sorted(values)
#                 count = len(sorted_values)

#                 return {
#                 "count": count,
#                 "min": min(sorted_values),
#                 "max": max(sorted_values),
#                 "avg": sum(sorted_values) / count,
#                 "p50": sorted_values[int(count * 0.5)],
#                 "p90": sorted_values[int(count * 0.9)],
#                 "p95": sorted_values[int(count * 0.95)],
#                 "p99": sorted_values[int(count * 0.99)],
#                 }

#     def record_request(self, response_time: float, success: bool = True):
#         """""""""
#         with self.lock:
#             self.request_count += 1
#             self.total_response_time += response_time

#             if not success:
#                 self.error_count += 1

#                 self.record_timer("request_duration", response_time)
#                 self.increment_counter("requests_total")

#             if not success:
#                 self.increment_counter("errors_total")

#     def get_summary(self) -> dict[str, Any]:
#         """""""""
#         with self.lock:
#             uptime = time.time() - self.start_time
#             avg_response_time = (
#                 self.total_response_time / self.request_count
#                 if self.request_count > 0:
#                     else 0.0:
#                     )
#                     error_rate = (
#                     self.error_count / self.request_count if self.request_count > 0 else 0.0
#                     )

#                     return {
#                     "uptime_seconds": uptime,
#                     "requests_total": self.request_count,
#                     "errors_total": self.error_count,
#                     "error_rate": error_rate,
#                     "avg_response_time": avg_response_time,
#                     "counters": dict(self.counters),
#                     "gauges": dict(self.gauges),
#                     "timer_stats": {
#                     name: self.get_timer_stats(name) for name in self.timers
#                     },
#                     }

#     def reset(self):
#         """""""""
#         with self.lock:
#             self.metrics.clear()
#             self.counters.clear()
#             self.gauges.clear()
#             self.timers.clear()
#             self.request_count = 0
#             self.error_count = 0
#             self.total_response_time = 0.0
#             self.start_time = time.time()

    #  AgentManager 
#     def update_active_sessions(self, count: int):
#         """""""""
#         self.set_gauge("active_sessions", float(count))

#     def increment_chat_message_count(self, direction: str, message_type: str):
#         """""""""
#         tags = {"direction": direction, "type": message_type}
#         self.increment_counter("chat_messages_total", 1.0, tags)

#     def increment_session_count(self, action: str):
#         """""""""
#         tags = {"action": action}
#         self.increment_counter("sessions_total", 1.0, tags)

#     def track_multimodal_process(:
#         self, input_type: str, status: str, latency: float, input_size: int
#         ):
#         """""""""
#         tags = {"input_type": input_type, "status": status}
#         self.increment_counter("multimodal_processes_total", 1.0, tags)
#         self.record_timer("multimodal_process_duration", latency, tags)
#         self.set_gauge("multimodal_input_size_bytes", float(input_size), tags)

#     def increment_active_requests(self, endpoint: str):
#         """""""""
#         tags = {"endpoint": endpoint}
#         self.increment_counter("active_requests", 1.0, tags)
#         current_active = self.get_gauge(f"active_requests_{endpoint}")
#         self.set_gauge(f"active_requests_{endpoint}", current_active + 1)

#     def decrement_active_requests(self, endpoint: str):
#         """""""""
#         tags = {"endpoint": endpoint}
#         self.increment_counter("active_requests", -1.0, tags)
#         current_active = self.get_gauge(f"active_requests_{endpoint}")
#         self.set_gauge(f"active_requests_{endpoint}", max(0, current_active - 1))

#     def track_request(:
#         self, protocol: str, endpoint: str, status_code: int, latency: float
#         ):
#         """""""""
#         tags = {"protocol": protocol, "endpoint": endpoint, "status": str(status_code)}
#         self.increment_counter("requests_total", 1.0, tags)
#         self.record_timer("request_duration", latency, tags)

#         if status_code >= 400:
#             self.increment_counter("errors_total", 1.0, tags)


# class PerformanceTimer:
#     """""""""

#     def __init__(:
#         _self,
#         metric_s_collector: Metric_sCollector,
#         name: _str,
#         tag_s: Optional[Dict[_str, _str]] = None,
#         ):
#         self.metrics_collector = metrics_collector
#         self.name = name
#         self.tags = tags or {}
#         self.start_time = None

#     def __enter__(self):
#         self.start_time = time.time()
#         return self

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if self.start_time: duration = time.time() - self.start_time:
#             self.metrics_collector.record_timer(self.name, duration, self.tags)

            # /
#             success = exc_type is None
#             self.metrics_collector.record_request(duration, success)


# class AsyncPerformanceTimer:
#     """""""""

#     def __init__(:
#         _self,
#         metric_s_collector: Metric_sCollector,
#         name: _str,
#         tag_s: Optional[Dict[_str, _str]] = None,
#         ):
#         self.metrics_collector = metrics_collector
#         self.name = name
#         self.tags = tags or {}
#         self.start_time = None

#         async def __aenter__(self):
#         self.start_time = time.time()
#         return self

#         async def __aexit__(self, exc_type, exc_val, exc_tb):
#         if self.start_time: duration = time.time() - self.start_time:
#             self.metrics_collector.record_timer(self.name, duration, self.tags)

            # /
#             success = exc_type is None
#             self.metrics_collector.record_request(duration, success)


# 
#             _global_metrics_collector: MetricsCollector | None = None


# def get_metrics_collector() -> MetricsCollector:
#     """""""""
#     global _global_metrics_collector  # noqa: PLW0603
#     if _global_metrics_collector is None: _global_metrics_collector = MetricsCollector():
#         return _global_metrics_collector


# def timer(name: _str, tag_s: Optional[Dict[_str, _str]] = None) -> PerformanceTimer:
#     """""""""
#     return PerformanceTimer(get_metrics_collector(), name, tags)


# def a_sync_timer(:
#     name: _str, tag_s: Optional[Dict[_str, _str]] = None
#     ) -> AsyncPerformanceTimer:
#     """""""""
#     return AsyncPerformanceTimer(get_metrics_collector(), name, tags)


# def increment(name: _str, value: float = 1.0, tag_s: Optional[Dict[_str, _str]] = None):
#     """""""""
#     get_metrics_collector().increment_counter(name, value, tags)


# def gauge(name: _str, value: float, tag_s: Optional[Dict[_str, _str]] = None):
#     """""""""
#     get_metrics_collector().set_gauge(name, value, tags)


# def record_time(name: _str, duration: float, tag_s: Optional[Dict[_str, _str]] = None):
#     """""""""
#     get_metrics_collector().record_timer(name, duration, tags)


# def track_db_m_etrics(:
#     db_typ_e: Optional[str] = None,
#     op_eration: Optional[str] = None,
#     tabl_e: Optional[str] = None,
#     ):
#     """""""""

#     def decorator(func):
#         def wrapper(*args, **kwargs): start_time = time.time():
#             try:
#                 result = func(*args, **kwargs)
#                 success = True
#                 return result
#             except Exception:
#                 success = False
#                 raise
#             finally:
#                 duration = time.time() - start_time

                # 
#                 tags = {}
#                 if db_type: tags["db_type"] = db_type:
#                 if operation:
#                     tags["operation"] = operation
#                 if table:
#                     tags["table"] = table

                # 
#                     increment("db_operations_total", 1.0, tags)
#                     record_time("db_operation_duration", duration, tags)

#                 if success:
#                     increment("db_operations_success_total", 1.0, tags)
#                 else:
#                     increment("db_operations_error_total", 1.0, tags)

#                     logger.debug(
#                     f": {db_type} {operation} on {table}, : {success}, : {duration:.3f}s"
#                     )

#                     return wrapper

#                     return decorator


# def track_api_metrics(endpoint: str, method: str, status_code: int, duration: float):
#     """API""""""
#     tags = {"endpoint": endpoint, "method": method, "status_code": str(status_code)}

    # API
#     increment("api_requests_total", 1.0, tags)

    # 
#     record_time("api_request_duration", duration, tags)

    # 
#     if status_code >= 400:
#         increment("api_errors_total", 1.0, tags)

#         logger.debug(
#         f"API: {method} {endpoint}, : {status_code}, : {duration}s"
#         )


# def track_cach_e_m_etrics(:
#     op_eration: str, hit: Optional[bool] = None, siz_e: Optional[int] = None
#     ):
#     """""""""
#     tags = {"operation": operation}

    # 
#     increment("cache_operations_total", 1.0, tags)

    # /
#     if hit is not None:
#         if hit:
#             increment("cache_hits_total", 1.0, tags)
#         else:
#             increment("cache_misses_total", 1.0, tags)

    # 
#     if size is not None:
#         gauge("cache_size_bytes", float(size), tags)

#         logger.debug(f": {operation}, : {hit}, : {size}")


# def track_device_metrics(:
#     device_type: str, operatio_n: str, success: bool, duratio_n: Optio_nal[float] = No_ne
#     ):
#     """""""""
#     tags = {"device_type": device_type, "operation": operation, "success": str(success)}

    # 
#     increment("device_operations_total", 1.0, tags)

    # /
#     if success:
#         increment("device_operations_success_total", 1.0, tags)
#     else:
#         increment("device_operations_error_total", 1.0, tags)

    # 
#     if duration is not None: record_time("device_operation_duration", duration, tags):

#         logger.debug(
#         f": {device_type} {operation}, : {success}, : {duration}s"
#         )


# def track_age_nt_metrics(:
#     age_nt__name: str, actio_n: str, success: bool, duratio_n: Optio_nal[float] = No_ne
#     ):
#     """""""""
#     tags = {"agent": agent_name, "action": action, "success": str(success)}

    # 
#     increment("agent_operations_total", 1.0, tags)

    # /
#     if success:
#         increment("agent_operations_success_total", 1.0, tags)
#     else:
#         increment("agent_operations_error_total", 1.0, tags)

    # 
#     if duration is not None: record_time("agent_operation_duration", duration, tags):

#         logger.debug(
#         f": {agent_name} {action}, : {success}, : {duration}s"
#         )


# def track_llm_metric_s(:
#     model: Optional[_str] = None,
#     model_name: Optional[_str] = None,
#     operation: Optional[_str] = None,
#     query_type: Optional[_str] = None,
#     token_s: Optional[int] = None,
#     ):
#     """""""""

#     def decorator(func):
#         def wrapper(*args, **kwargs): start_time = time.time():
#             try:
#                 result = func(*args, **kwargs)
#                 success = True
#                 return result
#             except Exception:
#                 success = False
#                 raise
#             finally:
#                 duration = time.time() - start_time

                # 
#                 tags = {}
                # 
#                 model_value = model or model_name
#                 operation_value = operation or query_type

#                 if model_value: tags["model"] = model_value:
#                 if operation_value: tags["operation"] = operation_value:

                # 
#                     increment("llm_operations_total", 1.0, tags)
#                     record_time("llm_operation_duration", duration, tags)

#                 if tokens:
#                     increment("llm_tokens_total", float(tokens), tags)
#                     gauge()
#                         "llm_tokens_per_second",
#                         float(tokens) / duration if duration > 0 else 0,
#                         tags,
#                     )

#                 if success:
#                     increment("llm_operations_success_total", 1.0, tags)
#                 else:
#                     increment("llm_operations_error_total", 1.0, tags)

#                     logger.debug(
#                     f"LLM: {model_value} {operation_value}, : {success}, : {duration:.3f}s, tokens: {tokens}"
#                     )

#                     return wrapper

#                     return decorator


#                     def track_service_call_metrics(service: str, metho_d: Optional[str] = None):
#     """""""""

#     def decorator(func):
#         def wrapper(*args, **kwargs): start_time = time.time():
#             success = True
#             error_type = None

#             try:
#                 result = func(*args, **kwargs)
#                 return result
#             except Exception as e:
#                 success = False
#                 error_type = type(e).__name__
#                 raise
#             finally:
#                 duration = time.time() - start_time

                # 
#                 collector = get_metrics_collector()
#                 tags = {
#                     "service": service,
#                     "method": method or func.__name__,
#                     "success": str(success).lower(),
#                 }

#                 if error_type: tags["error_type"] = error_type:

#                     collector.record_timer("service_call_duration", duration, tags)
#                     collector.increment_counter("service_calls_total", 1.0, tags)

#                 if not success:
#                     collector.increment_counter("service_call_errors_total", 1.0, tags)

#                     logger.debug(
#                     f": {service}.{method or func.__name__}, : {success}, : {duration:.3f}s"
#                     )

#                     return wrapper

#                     return decorator


#                     def track_request_metrics(en_dpoint: Optional[str] = None, metho_d: Optional[str] = None):
#     """""""""

#     def decorator(func):
#         def wrapper(*args, **kwargs): start_time = time.time():
#             success = True
#             error_type = None
#             status_code = 200

#             try:
#                 result = func(*args, **kwargs)
#                 return result
#             except Exception as e:
#                 success = False
#                 error_type = type(e).__name__
#                 status_code = 500
#                 raise
#             finally:
#                 duration = time.time() - start_time

                # 
#                 collector = get_metrics_collector()
#                 tags = {
#                     "endpoint": endpoint or func.__name__,
#                     "method": method or "unknown",
#                     "status_code": str(status_code),
#                     "success": str(success).lower(),
#                 }

#                 if error_type: tags["error_type"] = error_type:

#                     collector.record_timer("request_duration", duration, tags)
#                     collector.increment_counter("requests_total", 1.0, tags)

#                 if not success:
#                     collector.increment_counter("request_errors_total", 1.0, tags)

#                     logger.debug(
#                     f": {method} {endpoint}, : {status_code}, : {duration:.3f}s"
#                     )

#                     return wrapper

#                     return decorator


#  AgentManager 
# def update_active_sessions(count: int):
#     """""""""
#     gauge("active_sessions", float(count))


# def increment_chat_message_count(direction: str, message_type: str):
#     """""""""
#     tags = {"direction": direction, "type": message_type}
#     increment("chat_messages_total", 1.0, tags)


# def increment_session_count(action: str):
#     """""""""
#     tags = {"action": action}
#     increment("sessions_total", 1.0, tags)


# def track_multimodal_process(:
#     input_type: str, status: str, latency: float, input_size: int
#     ):
#     """""""""
#     tags = {"input_type": input_type, "status": status}
#     increment("multimodal_processes_total", 1.0, tags)
#     record_time("multimodal_process_duration", latency, tags)
#     gauge("multimodal_input_size_bytes", float(input_size), tags)
