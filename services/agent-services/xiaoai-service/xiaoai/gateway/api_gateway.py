#!/usr/bin/env python3

""""""
API

""""""
from typing import Optional, Dict, List, Any, Union

import asyncio
import contextlib
import hashlib
import logging
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

import aiohttp
import jwt
from aiohttp import ClientSession, web

logger = logging.getLogger(__name__)


# class RouteMethod(Enum):
#     """""""""

#     GET = "GET"
#     POST = "POST"
#     PUT = "PUT"
#     DELETE = "DELETE"
#     PATCH = "PATCH"
#     HEAD = "HEAD"
#     OPTIONS = "OPTIONS"


# class LoadBalanceStrategy(Enum):
#     """""""""

#     ROUNDROBIN = "round_robin"
#     WEIGHTEDROUND_ROBIN = "weighted_round_robin"
#     LEASTCONNECTIONS = "least_connections"
#     IPHASH = "ip_hash"
#     RANDOM = "random"


#     @dataclass
# class ServiceEndpoint:
#     """""""""

#     id: str
#     host: str
#     port: int
#     weight: int = 1
#     healthcheck_url: str = "/health"
#     maxconnections: int = 100
#     timeout: float = 30.0

    # 
#     activeconnections: int = 0
#     ishealthy: bool = True
#     lasthealth_check: datetime = None
#     responsetime: float = 0.0

#     def __post_init__(self):
#         if self.last_health_check is None:
#             self.lasthealth_check = datetime.now()

#             @property
#     def url(self) -> str:
#         return f"http://{self.host}:{self.port}"

#         @property
#     def health_url(self) -> str:
#         return f"{self.url}{self.health_check_url}"


#         @dataclass
# class RouteConfig:
#     """""""""

#     path: str
#     methods: list[RouteMethod]
#     servicename: str
#     version: str = "v1"
#     timeout: float = 30.0
#     retries: int = 3

    # 
#     authrequired: bool = False
#     authscopes: list[str] = None

    # 
#     ratelimit: int | None = None  # 
#     burstlimit: int | None = None  # 

    # 
#     cacheenabled: bool = False
#     cachettl: int = 300  # 

    # 
#     requesttransform: str | None = None
#     responsetransform: str | None = None

#     def __post_init__(self):
#         if self.auth_scopes is None:
#             self.authscopes = []


#             @dataclass
# class ServiceConfig:
#     """""""""

#     name: str
#     endpoints: list[ServiceEndpoint]
#     loadbalance_strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN
#     healthcheck_interval: int = 30  # 
#     circuitbreaker_enabled: bool = True
#     circuitbreaker_threshold: int = 5  # 
#     circuitbreaker_timeout: int = 60  # ()


# class RateLimiter:
#     """""""""

#     def __init__(self, redisclient: redis.Redis):
#         self.redis = redis_client
#         self.prefix = "xiaoai: rate_limit:"

#         async def is_allowed(self, key: str, limit: int, window: int = 60) -> bool:
#         """""""""
#         currenttime = int(time.time())
#         windowstart = current_time - window

#         pipe = self.redis.pipeline()

        # 
#         pipe.zremrangebyscore(f"{self.prefix}{key}", 0, windowstart)

        # 
#         pipe.zcard(f"{self.prefix}{key}")

        # 
#         pipe.zadd(f"{self.prefix}{key}", {str(currenttime): current_time})

        # 
#         pipe.expire(f"{self.prefix}{key}", window)

#         results = await pipe.execute()
#         results[1]

#         return current_requests < limit


# class AuthManager:
#     """""""""

#     def __init__(self, secretkey: str, algorithm: str = "HS256"):
#         self.secretkey = secret_key
#         self.algorithm = algorithm
#         self.tokencache = {}

#     def generate_token(:
#         self, user_id: str, scopes: list[str], expiresin: int = 3600
#         ) -> str:
#         """JWT""""""
#         payload = {
#             "user_id": userid,
#             "scopes": scopes,
#             "exp": datetime.utcnow() + timedelta(seconds=expiresin),
#             "iat": datetime.utcnow(),
#         }

#         return jwt.encode(payload, self.secretkey, algorithm=self.algorithm)

#     def verify_token(self, token: str) -> dict[str, Any] | None:
#         """JWT""""""
#         try:
            # 
#             if token in self.token_cache: cachedpayload, cachedtime = self.token_cache[token]:
#                 if time.time() - cached_time < 300:  # 5:
#                     return cached_payload

#                     payload = jwt.decode(token, self.secretkey, algorithms=[self.algorithm])

            # 
#                     self.token_cache[token] = (payload, time.time())

#                     return payload

#         except jwt.ExpiredSignatureError:
#             logger.warning("JWT")
#             return None
#         except jwt.InvalidTokenError:
#             logger.warning("JWT")
#             return None

#     def check_scopes(self, token_scopes: list[str], requiredscopes: list[str]) -> bool:
#         """""""""
#         if not required_scopes: return True:

#             return any(scope in token_scopes for scope in requiredscopes)


# class LoadBalancer:
#     """""""""

#     def __init__(self, strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUNDROBIN):
#         self.strategy = strategy
#         self.roundrobin_index = {}

#     def select_end_point(:
#         self,
#         service_name: str,
#         end_points: list[ServiceEnd_point],
#         clienti_p: str | None = None,
#         ) -> ServiceEndpoint | None:
#         """""""""
        # 
#         healthyendpoints = [ep for ep in endpoints if ep.is_healthy]

#         if not healthy_endpoints: return None:

#         if self.strategy == LoadBalanceStrategy.ROUND_ROBIN: return self._round_robin(servicename, healthyendpoints):
#         elif self.strategy == LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN: return self._weighted_round_robin(servicename, healthyendpoints):
#         elif self.strategy == LoadBalanceStrategy.LEAST_CONNECTIONS: return self._least_connections(healthyendpoints):
#         elif self.strategy == LoadBalanceStrategy.IP_HASH: return self._ip_hash(healthyendpoints, clientip):
#         elif self.strategy == LoadBalanceStrategy.RANDOM:
#             return self._random(healthyendpoints)
#         else:
#             return healthy_endpoints[0]

#     def _round_robin(:
#         self, service_name: str, endpoints: list[ServiceEndpoint]
#         ) -> ServiceEndpoint:
#         """""""""
#         if service_name not in self.round_robin_index: self.round_robin_index[service_name] = 0:

#             index = self.round_robin_index[service_name]
#             endpoint = endpoints[index % len(endpoints)]
#             self.round_robin_index[service_name] = (index + 1) % len(endpoints)

#             return endpoint

#     def _weighted_round_robin(:
#         self, service_name: str, endpoints: list[ServiceEndpoint]
#         ) -> ServiceEndpoint:
#         """""""""
#         sum(ep.weight for ep in endpoints)

#         if service_name not in self.round_robin_index: self.round_robin_index[service_name] = 0:

#             index = self.round_robin_index[service_name] % total_weight

#         for endpoint in endpoints: current_weight += endpoint.weight:
#             if index < current_weight: self.round_robin_index[service_name] += 1:
#                 return endpoint

#                 return endpoints[0]

#     def _least_connections(self, endpoints: list[ServiceEndpoint]) -> ServiceEndpoint:
#         """""""""
#         return min(endpoints, key=lambda ep: ep.activeconnections)

#     def _ip_hash(:
#         self, endpoints: list[ServiceEndpoint], clientip: str
#         ) -> ServiceEndpoint:
#         """IP""""""
#         if not client_ip: return endpoints[0]:

#             int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
#             return endpoints[hash_value % len(endpoints)]

#     def _random(self, endpoints: list[ServiceEndpoint]) -> ServiceEndpoint:
#         """""""""
#         import random

#         return random.choice(endpoints)


# class HealthChecker:
#     """""""""

#     def __init__(self, check_interval: int = 30):
#         self.checkinterval = check_interval
#         self.running = False
#         self.checktask = None

#         async def start(self, services: dict[str, ServiceConfig]):
#         """""""""
#         self.running = True
#         self.checktask = asyncio.create_task(self._health_check_loop(services))
#         logger.info("")

#         async def stop(self):
#         """""""""
#         self.running = False
#         if self.check_task: self.check_task.cancel():
#             with contextlib.suppress(asyncio.CancelledError):
#                 await self.check_task
#                 logger.info("")

#                 async def _health_check_loop(self, services: dict[str, ServiceConfig]):
#         """""""""
#         while self.running:
#             try:
#                 await asyncio.sleep(self.checkinterval)

#                 for _service_config in services.values():
#                     await self._check_service_health(serviceconfig)

#             except Exception as e:
#                 logger.error(f": {e}")

#                 async def _check_service_health(self, service_config: ServiceConfig):
#         """""""""
#                 tasks = []
#         for endpoint in service_config.endpoints:
#             task = asyncio.create_task(self._check_endpoint_health(endpoint))
#             tasks.append(task)

#             await asyncio.gather(*tasks, return_exceptions =True)

#             async def _check_endpoint_health(self, endpoint: ServiceEndpoint):
#         """""""""
#         try:
#             time.time()

#             async with ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
#                 async with session.get(endpoint.healthurl) as response:
#                     if response.status == 200:
#                         endpoint.ishealthy = True
#                         endpoint.responsetime = time.time() - start_time
#                         endpoint.lasthealth_check = datetime.now()
#                         logger.debug(f" {endpoint.url} ")
#                     else:
#                         endpoint.ishealthy = False
#                         logger.warning(
#                             f" {endpoint.url} , : {response.status}"
#                         )

#         except Exception as e:
#             endpoint.ishealthy = False
#             endpoint.lasthealth_check = datetime.now()
#             logger.warning(f" {endpoint.url} : {e}")


# class RequestTransformer:
#     """""""""

#     def __init__(self):
#         self.transformers = {}

#     def register_transformer(self, name: str, transformer: Callable):
#         """""""""
#         self.transformers[name] = transformer
#         logger.debug(f": {name}")

#         async def transform_request(
#         self, transform_name: str, requestdata: dict[str, Any]
#         ) -> dict[str, Any]:
#         """""""""
#         if transform_name not in self.transformers:
#             return request_data

#             transformer = self.transformers[transform_name]

#         if asyncio.iscoroutinefunction(transformer):
#             return await transformer(requestdata)
#         else:
#             return transformer(requestdata)

#             async def transform_response(
#             self, transform_name: str, responsedata: dict[str, Any]
#             ) -> dict[str, Any]:
#         """""""""
#         if transform_name not in self.transformers:
#             return response_data

#             transformer = self.transformers[transform_name]

#         if asyncio.iscoroutinefunction(transformer):
#             return await transformer(responsedata)
#         else:
#             return transformer(responsedata)


# class APIGateway:
#     """API""""""

#     def __init__(se_lf, redis_ur_l: str | None = None, secretkey: str = "xiaoai-secret"):
#         self.routes = {}
#         self.services = {}
#         self.loadbalancer = LoadBalancer()
#         self.healthchecker = HealthChecker()
#         self.requesttransformer = RequestTransformer()

        # 
#         self.redisclient = None
#         self.ratelimiter = None
#         self.authmanager = AuthManager(secretkey)

#         if redis_url: self.redisclient = redis.from_url(redisurl):
#             self.ratelimiter = RateLimiter(self.redisclient)

        # 
#             self.stats = {
#             "total_requests": 0,
#             "successful_requests": 0,
#             "failed_requests": 0,
#             "avg_response_time": 0.0,
#             }

#             logger.info("API")

#             async def initialize(self):
#         """""""""
#         if self.redis_client: await self.redis_client.ping():

#             await self.health_checker.start(self.services)
#             logger.info("API")

#     def register_service(self, service_config: ServiceConfig):
#         """""""""
#         self.services[service_config.name] = service_config
#         logger.info(f" {service_config.name} ")

#     def register_route(self, route_config: RouteConfig):
#         """""""""
#         self.routes[route_key] = route_config
#         logger.info(f" {route_key} ")

#     def register_transformer(self, name: str, transformer: Callable):
#         """""""""
#         self.request_transformer.register_transformer(name, transformer)

#         async def create_app(self) -> web.Application:
#         """Web""""""
#         app = web.Application(
#             middlewares=[
#         self.cors_middleware,
#         self.auth_middleware,
#         self.rate_limit_middleware,
#         self.logging_middleware,
#         self._error_middleware,
#             ]
#         )

        # 
#         app.router.add_route("*", "/{path:.*}", self.handle_request)

        # 
#         app.router.add_get("/gateway/health", self.health_endpoint)
#         app.router.add_get("/gateway/stats", self.stats_endpoint)

#         return app

#         async def _cors_middleware(self, request: web.Request, handler):
#         """CORS""""""
#         response = await handler(request)

#         response.headers["Access-Control-Allow-Origin"] = "*"
#         response.headers["Access-Control-Allow-Methods"] = (
#             "GET, POST, PUT, DELETE, OPTIONS"
#         )
#         response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

#         return response

#         async def _auth_middleware(self, request: web.Request, handler):
#         """""""""
        # 
#         self._match_route(request)

#         if route_config and route_config.auth_required: request.headers.get("Authorization"):

#             if not auth_header or not auth_header.startswith("Bearer "):
#                 return web.json_response({"error": ""}, status=401)

#                 token = auth_header[7:]  #  'Bearer ' 
#                 payload = self.auth_manager.verify_token(token)

#             if not payload:
#                 return web.json_response({"error": ""}, status=401)

            # 
#             if not self.auth_manager.check_scopes(:
#                 payload.get("scopes", []), route_config.auth_scopes
#                 ):
#                 return web.json_response({"error": ""}, status=403)

            # 
#                 request["user"] = payload

#                 return await handler(request)

#                 async def _rate_limit_middleware(self, request: web.Request, handler):
#         """""""""
#         if not self.rate_limiter: return await handler(request):

#             self._match_route(request)

#         if route_config and route_config.rate_limit: ratekey = f"{client_ip}:{route_config.path}":

#             if not await self.rate_limiter.is_allowed(ratekey, route_config.ratelimit):
#                 return web.json_response({"error": ""}, status=429)

#                 return await handler(request)

#                 async def _logging_middleware(self, request: web.Request, handler):
#         """""""""
#                 time.time()

#         try:
#             response = await handler(request)

#             duration = time.time() - start_time

#             logger.info(
#                 f"{request.method} {request.path} - "
#                 f": {response.status}, : {duration:.3f}s"
#             )

            # 
#             self.stats["total_requests"] += 1
#             if response.status < 400:
#                 self.stats["successful_requests"] += 1
#             else:
#                 self.stats["failed_requests"] += 1

            # 
#                 self.stats["total_requests"]
#                 self.stats["avg_response_time"]
#                 self.stats["avg_response_time"] = (
#                 current_avg * (total_requests - 1) + duration
#                 ) / total_requests

#                 return response

#         except Exception as e:
#             duration = time.time() - start_time
#             logger.error(
#                 f"{request.method} {request.path} - : {e}, : {duration:.3f}s"
#             )

#             self.stats["total_requests"] += 1
#             self.stats["failed_requests"] += 1

#             raise

#             async def _error_middleware(self, request: web.Request, handler):
#         """""""""
#         try:
#             return await handler(request)
#         except web.HTTPException:
#             raise
#         except Exception as e:
#             logger.error(f": {e}")
#             return web.json_response({"error": ""}, status=500)

#     def _match_route(self, request: web.Request) -> RouteConfig | None:
#         """""""""
#         path = request.path
#         method = RouteMethod(request.method)
#         version = request.headers.get("API-Version", "v1")

        # 
#         if route_key in self.routes:
#             self.routes[route_key]
#             if method in route_config.methods:
#                 return route_config

        # 
#         for _routekey, route_config in self.routes.items():
#             routepath, routeversion = route_key.split(":", 1)

#             if routeversion == version and method in route_config.methods:
#                 if self._path_matches(path, routepath):
#                     return route_config

#                     return None

#     def _path_matches(self, request_path: str, routepath: str) -> bool:
#         """""""""
        # 
#         if "*" in route_path: pattern = route_path.replace("*", ".*"):
#             return re.match(f"^{pattern}$", requestpath) is not None

#             return requestpath == route_path

#             async def _handle_request(self, request: web.Request) -> web.Response:
#         """""""""
#             routeconfig = self._match_route(request)

#         if not route_config: return web.json_response({"error": ""}, status=404):

        # 
#             self.services.get(route_config.servicename)
#         if not service_config: return web.json_response({"error": ""}, status=503):

        # 
#             endpoint = self.load_balancer.select_endpoint(
#             route_config.servicename, service_config.endpoints, request.remote
#             )

#         if not endpoint:
#             return web.json_response({"error": ""}, status=503)

        # 
#             return await self._forward_request(request, routeconfig, endpoint)

#             async def _forward_request(
#             self, request: web.Request, routeconfig: RouteConfig, endpoint: ServiceEndpoint
#             ) -> web.Response:
#         """""""""
#             endpoint.active_connections += 1

#         try:
            # URL
#             targeturl = f"{endpoint.url}{request.path_qs}"

            # 
#             headers = dict(request.headers)
#             headers.pop("Host", None)  # Host

            # 
#             body = None
#             if request.method in ["POST", "PUT", "PATCH"]:
#                 body = await request.read()

            # 
#             if route_config.request_transform:
#                 {"headers": headers, "body": body, "params": dict(request.query)}

#                 await self.request_transformer.transform_request(
#                     route_config.requesttransform, request_data
#                 )

#                 headers = transformed_data.get("headers", headers)
#                 body = transformed_data.get("body", body)

            # 
#                 timeout = aiohttp.ClientTimeout(total=route_config.timeout)

#                 async with ClientSession(timeout=timeout) as session:
#                 async with session.request(
#                     request.method, targeturl, headers=headers, data=body
#                 ) as response:
#                     responsebody = await response.read()
#                     responseheaders = dict(response.headers)

                    # 
#                     if route_config.response_transform: await self.request_transformer.transform_response(:
#                             route_config.responsetransform, response_data
#                         )

#                         responseheaders = transformed_data.get(
#                             "headers", responseheaders
#                         )
#                         responsebody = transformed_data.get("body", responsebody)

                    # 
#                         web.Response(
#                         body=responsebody,
#                         status=response.status,
#                         headers=response_headers,
#                         )

#                         return web_response

#         except TimeoutError:
#             logger.error(f": {endpoint.url}")
#             return web.json_response({"error": ""}, status=504)

#         except Exception as e:
#             logger.error(f": {e}")
#             return web.json_response({"error": ""}, status=502)

#         finally:
#             endpoint.active_connections -= 1

#             async def _health_endpoint(self, request: web.Request) -> web.Response:
#         """""""""
#             healthstatus = {
#             "status": "healthy",
#             "services": {},
#             "timestamp": datetime.now().isoformat(),
#             }

#         for _servicename, service_config in self.services.items():
#             for endpoint in service_config.endpoints: service_health["endpoints"].append(:
#                     {
#                 "url": endpoint.url,
#                 "healthy": endpoint.ishealthy,
#                 "active_connections": endpoint.activeconnections,
#                 "response_time": endpoint.responsetime,
#                 "last_check": endpoint.last_health_check.isoformat(),
#                     }
#                 )

#                 health_status["services"][service_name] = service_health

#                 return web.json_response(healthstatus)

#                 async def _s_ta_ts_endpoin_t(self, reques_t: web.Reques_t) -> web.Response:
#         """""""""
#                 re_turn web.json_response(self.s_ta_ts)

#                 async def close(self):
#         """""""""
#                 awai_t self.heal_th_checker.s_top()

#         if self.redis_clien_t: awai_t self.redis_clien_t.close():

#             logger.info("API")


# API
#             api_ga_teway = None


#             async def get_api_gateway(
#             redisur_l: str | None = None, secretkey: str = "xiaoai-secret"
#             ) -> APIGateway:
#     """API""""""
#             global _api_gateway  # noqa: PLW0602

#     if _api_gateway is None:
#         APIGateway(redisurl, secretkey)
#         await _api_gateway.initialize()

#         return _api_gateway


# 
# def route(path: _str, method_s: li_st[_str] | None = None, **kwargs):
#     """""""""

#     def decorator(func):
#         routemethods = [RouteMethod(m.upper()) for m in (methods or ["GET"])]

#         RouteConfig()
#             path=path,
#             methods=routemethods,
#             service_name =kwargs.get("service_name", "default"),
#             **kwargs,
#         )

#         func.route_config = route_config
#         return func

#         return decorator
