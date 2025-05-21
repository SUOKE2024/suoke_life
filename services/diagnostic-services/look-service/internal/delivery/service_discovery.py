#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务发现模块 - 实现服务注册与发现

本模块提供了基于Consul和Etcd的服务注册与发现机制，支持自动化的服务
注册、健康检查集成、服务节点动态更新以及服务实例负载均衡，确保微服务
架构中的服务能够可靠地相互发现和通信。
"""

import os
import time
import json
import uuid
import socket
import logging
import threading
from typing import Dict, List, Optional, Tuple, Any, Callable

import grpc
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ConsulServiceRegistry:
    """基于Consul的服务注册与发现"""
    
    def __init__(self, config: Dict):
        """
        初始化Consul服务注册器
        
        Args:
            config: 配置字典
        """
        self.config = config
        
        # Consul连接参数
        self.consul_host = config.get('consul_host', 'localhost')
        self.consul_port = config.get('consul_port', 8500)
        self.consul_token = config.get('consul_token', '')
        self.consul_scheme = config.get('consul_scheme', 'http')
        
        # 服务信息
        self.service_name = config.get('service_name', 'look-service')
        self.service_id = config.get('service_id', f"{self.service_name}-{str(uuid.uuid4())[:8]}")
        self.service_port = config.get('service_port', 50051)
        self.service_address = config.get('service_address', self._get_host_ip())
        self.service_tags = config.get('service_tags', ['grpc', 'tcm', 'look'])
        
        # 健康检查参数
        self.check_interval = config.get('check_interval', '15s')
        self.check_timeout = config.get('check_timeout', '5s')
        self.check_deregister_after = config.get('check_deregister_after', '30s')
        
        # 内部状态
        self._is_registered = False
        self._consul_client = None
        self._heartbeat_thread = None
        self._stop_event = threading.Event()
        
        logger.info(f"Consul服务注册器初始化完成: {self.service_id}")
    
    def register(self) -> bool:
        """
        注册服务到Consul
        
        Returns:
            bool: 注册是否成功
        """
        if self._is_registered:
            logger.warning(f"服务已注册: {self.service_id}")
            return True
            
        try:
            import consul
            
            # 创建Consul客户端
            self._consul_client = consul.Consul(
                host=self.consul_host,
                port=self.consul_port,
                token=self.consul_token,
                scheme=self.consul_scheme
            )
            
            # 构建健康检查配置
            check = {
                'id': f"health-{self.service_id}",
                'name': f"Health check for {self.service_name}",
                'grpc': f"{self.service_address}:{self.service_port}",
                'interval': self.check_interval,
                'timeout': self.check_timeout,
                'DeregisterCriticalServiceAfter': self.check_deregister_after
            }
            
            # 注册服务
            logger.info(f"正在注册服务到Consul: {self.service_id}")
            result = self._consul_client.agent.service.register(
                name=self.service_name,
                service_id=self.service_id,
                address=self.service_address,
                port=self.service_port,
                tags=self.service_tags,
                check=check
            )
            
            if result:
                self._is_registered = True
                logger.info(f"服务成功注册到Consul: {self.service_id}")
                
                # 启动心跳线程
                self._start_heartbeat()
                
                # 注册服务元数据
                self._register_metadata()
                
                return True
            else:
                logger.error(f"注册服务到Consul失败: {self.service_id}")
                return False
                
        except ImportError:
            logger.error("未安装python-consul库，服务注册失败")
            return False
            
        except Exception as e:
            logger.error(f"注册服务到Consul发生错误: {str(e)}")
            return False
    
    def deregister(self) -> bool:
        """
        从Consul注销服务
        
        Returns:
            bool: 注销是否成功
        """
        if not self._is_registered or not self._consul_client:
            logger.warning(f"服务未注册，无需注销: {self.service_id}")
            return True
            
        try:
            # 停止心跳线程
            self._stop_heartbeat()
            
            # 注销服务
            logger.info(f"正在从Consul注销服务: {self.service_id}")
            result = self._consul_client.agent.service.deregister(self.service_id)
            
            if result is not False:  # 注意：成功返回None
                self._is_registered = False
                logger.info(f"服务成功从Consul注销: {self.service_id}")
                return True
            else:
                logger.error(f"从Consul注销服务失败: {self.service_id}")
                return False
                
        except Exception as e:
            logger.error(f"从Consul注销服务发生错误: {str(e)}")
            return False
    
    def get_service_instances(self, service_name: str) -> List[Dict]:
        """
        获取指定服务的所有实例
        
        Args:
            service_name: 服务名称
            
        Returns:
            List[Dict]: 服务实例列表
        """
        if not self._consul_client:
            logger.error("未连接到Consul，无法获取服务实例")
            return []
            
        try:
            # 查询服务实例
            _, services = self._consul_client.health.service(
                service=service_name,
                passing=True  # 只返回健康检查通过的实例
            )
            
            instances = []
            for service in services:
                service_data = service['Service']
                
                instance = {
                    'id': service_data['ID'],
                    'name': service_data['Service'],
                    'address': service_data['Address'],
                    'port': service_data['Port'],
                    'tags': service_data.get('Tags', []),
                    'meta': service_data.get('Meta', {})
                }
                
                instances.append(instance)
                
            logger.debug(f"发现服务 {service_name} 的 {len(instances)} 个实例")
            return instances
            
        except Exception as e:
            logger.error(f"获取服务实例失败: {str(e)}")
            return []
    
    def create_service_channel(
        self, 
        service_name: str,
        use_load_balancing: bool = True
    ) -> Optional[grpc.Channel]:
        """
        创建到指定服务的gRPC通道
        
        Args:
            service_name: 服务名称
            use_load_balancing: 是否使用负载均衡
            
        Returns:
            Optional[grpc.Channel]: gRPC通道对象
        """
        instances = self.get_service_instances(service_name)
        
        if not instances:
            logger.error(f"未找到服务 {service_name} 的实例")
            return None
            
        try:
            if use_load_balancing and len(instances) > 1:
                # 使用gRPC名称解析器和负载均衡
                target = f"consul:///{service_name}"
                resolver_config = {
                    'consul_address': f"{self.consul_host}:{self.consul_port}"
                }
                
                channel = grpc.insecure_channel(
                    target,
                    options=[
                        ('grpc.service_config', json.dumps({
                            'loadBalancingConfig': [{'round_robin': {}}]
                        }))
                    ]
                )
                return channel
            else:
                # 使用第一个实例直接连接
                instance = instances[0]
                target = f"{instance['address']}:{instance['port']}"
                return grpc.insecure_channel(target)
                
        except Exception as e:
            logger.error(f"创建gRPC通道失败: {str(e)}")
            return None
    
    def watch_service(
        self, 
        service_name: str, 
        callback: Callable[[List[Dict]], None]
    ) -> bool:
        """
        监视服务变化
        
        Args:
            service_name: 服务名称
            callback: 变化回调函数
            
        Returns:
            bool: 是否成功开始监视
        """
        if not self._consul_client:
            logger.error("未连接到Consul，无法监视服务")
            return False
            
        try:
            import consul.aio
            import asyncio
            
            async def watch_task():
                # 创建异步Consul客户端
                async_client = consul.aio.Consul(
                    host=self.consul_host,
                    port=self.consul_port,
                    token=self.consul_token,
                    scheme=self.consul_scheme
                )
                
                index = None
                while not self._stop_event.is_set():
                    try:
                        index, services = await async_client.health.service(
                            service=service_name,
                            passing=True,
                            index=index,
                            wait='30s'
                        )
                        
                        instances = []
                        for service in services:
                            service_data = service['Service']
                            
                            instance = {
                                'id': service_data['ID'],
                                'name': service_data['Service'],
                                'address': service_data['Address'],
                                'port': service_data['Port'],
                                'tags': service_data.get('Tags', []),
                                'meta': service_data.get('Meta', {})
                            }
                            
                            instances.append(instance)
                        
                        # 通知回调
                        callback(instances)
                        
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        logger.error(f"监视服务 {service_name} 发生错误: {str(e)}")
                        await asyncio.sleep(5)
            
            # 启动异步监视任务
            loop = asyncio.get_event_loop()
            asyncio.ensure_future(watch_task(), loop=loop)
            
            logger.info(f"开始监视服务 {service_name} 的变化")
            return True
            
        except ImportError:
            logger.error("未安装python-consul或asyncio库，无法监视服务")
            return False
            
        except Exception as e:
            logger.error(f"设置服务监视失败: {str(e)}")
            return False
    
    def put_key_value(self, key: str, value: str) -> bool:
        """
        存储键值对到Consul
        
        Args:
            key: 键
            value: 值
            
        Returns:
            bool: 是否成功存储
        """
        if not self._consul_client:
            logger.error("未连接到Consul，无法存储键值")
            return False
            
        try:
            result = self._consul_client.kv.put(key, value)
            if result:
                logger.debug(f"成功存储键值对: {key}")
                return True
            else:
                logger.error(f"存储键值对失败: {key}")
                return False
                
        except Exception as e:
            logger.error(f"存储键值对发生错误: {str(e)}")
            return False
    
    def get_key_value(self, key: str) -> Optional[str]:
        """
        从Consul获取键值
        
        Args:
            key: 键
            
        Returns:
            Optional[str]: 值
        """
        if not self._consul_client:
            logger.error("未连接到Consul，无法获取键值")
            return None
            
        try:
            _, data = self._consul_client.kv.get(key)
            
            if data:
                value = data['Value']
                if isinstance(value, bytes):
                    value = value.decode('utf-8')
                
                logger.debug(f"成功获取键值: {key}")
                return value
            else:
                logger.warning(f"键不存在: {key}")
                return None
                
        except Exception as e:
            logger.error(f"获取键值发生错误: {str(e)}")
            return None
    
    def _start_heartbeat(self):
        """启动心跳线程"""
        if self._heartbeat_thread is not None and self._heartbeat_thread.is_alive():
            logger.warning("心跳线程已启动")
            return
            
        self._stop_event.clear()
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        logger.debug("心跳线程已启动")
    
    def _stop_heartbeat(self):
        """停止心跳线程"""
        if self._heartbeat_thread is None or not self._heartbeat_thread.is_alive():
            logger.warning("心跳线程未启动")
            return
            
        self._stop_event.set()
        self._heartbeat_thread.join(timeout=5.0)
        logger.debug("心跳线程已停止")
    
    def _heartbeat_loop(self):
        """心跳循环"""
        try:
            logger.info(f"开始心跳维护服务: {self.service_id}")
            
            while not self._stop_event.is_set():
                try:
                    # 检查服务是否仍在Consul中注册
                    services = self._consul_client.agent.services()
                    
                    if self.service_id not in services:
                        logger.warning(f"服务 {self.service_id} 不在Consul中，尝试重新注册")
                        self.register()
                    
                    # 等待下一次心跳
                    self._stop_event.wait(60)  # 每60秒检查一次
                    
                except Exception as e:
                    logger.error(f"心跳检查发生错误: {str(e)}")
                    self._stop_event.wait(5)  # 发生错误时，等待5秒后重试
                    
        except Exception as e:
            logger.error(f"心跳线程异常退出: {str(e)}")
    
    def _register_metadata(self):
        """注册服务元数据"""
        if not self._consul_client or not self._is_registered:
            return
            
        try:
            # 服务元数据
            metadata = {
                'version': self.config.get('version', '1.0.0'),
                'environment': self.config.get('environment', 'development'),
                'api_version': self.config.get('api_version', 'v1'),
                'features': ','.join(self.config.get('features', ['look', 'face', 'tongue'])),
                'protocol': 'grpc'
            }
            
            # 将元数据存储在KV存储中
            prefix = f"services/{self.service_name}/{self.service_id}/"
            
            for key, value in metadata.items():
                self.put_key_value(f"{prefix}{key}", str(value))
                
            logger.info(f"服务元数据已注册: {self.service_id}")
            
        except Exception as e:
            logger.error(f"注册服务元数据发生错误: {str(e)}")
    
    def _get_host_ip(self) -> str:
        """获取主机IP地址"""
        try:
            # 尝试获取非回环IP地址
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # 此方法不需要真正的连接
                s.connect(('10.255.255.255', 1))
                ip = s.getsockname()[0]
            return ip
        except Exception:
            # 如果失败，使用默认回环地址
            return '127.0.0.1'

class EtcdServiceRegistry:
    """基于Etcd的服务注册与发现"""
    
    def __init__(self, config: Dict):
        """
        初始化Etcd服务注册器
        
        Args:
            config: 配置字典
        """
        self.config = config
        
        # Etcd连接参数
        self.etcd_hosts = config.get('etcd_hosts', [{'host': 'localhost', 'port': 2379}])
        self.etcd_user = config.get('etcd_user', '')
        self.etcd_password = config.get('etcd_password', '')
        self.etcd_ca_cert = config.get('etcd_ca_cert', '')
        
        # 服务信息
        self.service_name = config.get('service_name', 'look-service')
        self.service_id = config.get('service_id', f"{self.service_name}-{str(uuid.uuid4())[:8]}")
        self.service_port = config.get('service_port', 50051)
        self.service_address = config.get('service_address', self._get_host_ip())
        self.service_tags = config.get('service_tags', ['grpc', 'tcm', 'look'])
        
        # 租约参数
        self.lease_ttl = config.get('lease_ttl', 30)  # 秒
        
        # 内部状态
        self._is_registered = False
        self._etcd_client = None
        self._lease_id = None
        self._heartbeat_thread = None
        self._stop_event = threading.Event()
        
        logger.info(f"Etcd服务注册器初始化完成: {self.service_id}")
    
    def register(self) -> bool:
        """
        注册服务到Etcd
        
        Returns:
            bool: 注册是否成功
        """
        if self._is_registered:
            logger.warning(f"服务已注册: {self.service_id}")
            return True
            
        try:
            import etcd3
            
            # 创建Etcd客户端
            self._connect_etcd()
            
            if not self._etcd_client:
                return False
            
            # 创建租约
            self._lease_id = self._etcd_client.lease(self.lease_ttl)
            
            # 服务数据
            service_data = json.dumps({
                'id': self.service_id,
                'name': self.service_name,
                'address': self.service_address,
                'port': self.service_port,
                'tags': self.service_tags,
                'version': self.config.get('version', '1.0.0'),
                'protocol': 'grpc'
            })
            
            # 服务注册路径
            service_key = f"/services/{self.service_name}/{self.service_id}"
            
            # 注册服务
            logger.info(f"正在注册服务到Etcd: {self.service_id}")
            self._etcd_client.put(service_key, service_data, lease=self._lease_id)
            
            self._is_registered = True
            logger.info(f"服务成功注册到Etcd: {self.service_id}")
            
            # 启动心跳线程
            self._start_heartbeat()
            
            return True
                
        except ImportError:
            logger.error("未安装etcd3库，服务注册失败")
            return False
            
        except Exception as e:
            logger.error(f"注册服务到Etcd发生错误: {str(e)}")
            return False
    
    def deregister(self) -> bool:
        """
        从Etcd注销服务
        
        Returns:
            bool: 注销是否成功
        """
        if not self._is_registered or not self._etcd_client:
            logger.warning(f"服务未注册，无需注销: {self.service_id}")
            return True
            
        try:
            # 停止心跳线程
            self._stop_heartbeat()
            
            # 服务注册路径
            service_key = f"/services/{self.service_name}/{self.service_id}"
            
            # 删除服务注册信息
            logger.info(f"正在从Etcd注销服务: {self.service_id}")
            self._etcd_client.delete(service_key)
            
            # 撤销租约
            if self._lease_id:
                self._etcd_client.revoke_lease(self._lease_id)
                self._lease_id = None
            
            self._is_registered = False
            logger.info(f"服务成功从Etcd注销: {self.service_id}")
            
            return True
                
        except Exception as e:
            logger.error(f"从Etcd注销服务发生错误: {str(e)}")
            return False
    
    def get_service_instances(self, service_name: str) -> List[Dict]:
        """
        获取指定服务的所有实例
        
        Args:
            service_name: 服务名称
            
        Returns:
            List[Dict]: 服务实例列表
        """
        if not self._etcd_client:
            logger.error("未连接到Etcd，无法获取服务实例")
            return []
            
        try:
            # 服务前缀
            prefix = f"/services/{service_name}/"
            
            # 查询前缀下的所有键值
            instances = []
            results = self._etcd_client.get_prefix(prefix)
            
            for value, metadata in results:
                try:
                    service_data = json.loads(value.decode('utf-8'))
                    instances.append(service_data)
                except (json.JSONDecodeError, UnicodeDecodeError, Exception) as e:
                    logger.warning(f"解析服务数据失败: {str(e)}")
            
            logger.debug(f"发现服务 {service_name} 的 {len(instances)} 个实例")
            return instances
            
        except Exception as e:
            logger.error(f"获取服务实例失败: {str(e)}")
            return []
    
    def create_service_channel(
        self, 
        service_name: str,
        use_load_balancing: bool = True
    ) -> Optional[grpc.Channel]:
        """
        创建到指定服务的gRPC通道
        
        Args:
            service_name: 服务名称
            use_load_balancing: 是否使用负载均衡
            
        Returns:
            Optional[grpc.Channel]: gRPC通道对象
        """
        instances = self.get_service_instances(service_name)
        
        if not instances:
            logger.error(f"未找到服务 {service_name} 的实例")
            return None
            
        try:
            if use_load_balancing and len(instances) > 1:
                # 使用gRPC名称解析器和负载均衡
                from grpc_resolver import EtcdResolver
                
                # 注册Etcd解析器
                EtcdResolver.register()
                
                # 创建带负载均衡的通道
                target = f"etcd:///{service_name}"
                channel = grpc.insecure_channel(
                    target,
                    options=[
                        ('grpc.service_config', json.dumps({
                            'loadBalancingConfig': [{'round_robin': {}}]
                        }))
                    ]
                )
                return channel
            else:
                # 使用第一个实例直接连接
                instance = instances[0]
                target = f"{instance['address']}:{instance['port']}"
                return grpc.insecure_channel(target)
                
        except Exception as e:
            logger.error(f"创建gRPC通道失败: {str(e)}")
            return None
    
    def watch_service(
        self, 
        service_name: str, 
        callback: Callable[[List[Dict]], None]
    ) -> bool:
        """
        监视服务变化
        
        Args:
            service_name: 服务名称
            callback: 变化回调函数
            
        Returns:
            bool: 是否成功开始监视
        """
        if not self._etcd_client:
            logger.error("未连接到Etcd，无法监视服务")
            return False
            
        try:
            # 服务前缀
            prefix = f"/services/{service_name}/"
            
            # 创建监视回调
            def watch_callback(event):
                try:
                    # 获取当前所有实例
                    instances = self.get_service_instances(service_name)
                    
                    # 触发用户回调
                    callback(instances)
                    
                except Exception as e:
                    logger.error(f"处理服务变更回调失败: {str(e)}")
            
            # 设置监视
            watch_id = self._etcd_client.add_watch_prefix_callback(
                prefix,
                watch_callback
            )
            
            logger.info(f"开始监视服务 {service_name} 的变化")
            return True
            
        except Exception as e:
            logger.error(f"设置服务监视失败: {str(e)}")
            return False
    
    def put_key_value(self, key: str, value: str) -> bool:
        """
        存储键值对到Etcd
        
        Args:
            key: 键
            value: 值
            
        Returns:
            bool: 是否成功存储
        """
        if not self._etcd_client:
            logger.error("未连接到Etcd，无法存储键值")
            return False
            
        try:
            self._etcd_client.put(key, value)
            logger.debug(f"成功存储键值对: {key}")
            return True
                
        except Exception as e:
            logger.error(f"存储键值对发生错误: {str(e)}")
            return False
    
    def get_key_value(self, key: str) -> Optional[str]:
        """
        从Etcd获取键值
        
        Args:
            key: 键
            
        Returns:
            Optional[str]: 值
        """
        if not self._etcd_client:
            logger.error("未连接到Etcd，无法获取键值")
            return None
            
        try:
            result = self._etcd_client.get(key)
            
            if result[0]:
                value = result[0].decode('utf-8')
                logger.debug(f"成功获取键值: {key}")
                return value
            else:
                logger.warning(f"键不存在: {key}")
                return None
                
        except Exception as e:
            logger.error(f"获取键值发生错误: {str(e)}")
            return None
    
    def _connect_etcd(self):
        """连接到Etcd服务器"""
        try:
            import etcd3
            
            hosts = []
            for host_info in self.etcd_hosts:
                host = host_info.get('host', 'localhost')
                port = host_info.get('port', 2379)
                hosts.append((host, port))
            
            # 选择第一个节点连接
            host, port = hosts[0]
            
            # 创建Etcd客户端
            if self.etcd_user and self.etcd_password:
                # 使用用户名密码认证
                self._etcd_client = etcd3.client(
                    host=host,
                    port=port,
                    user=self.etcd_user,
                    password=self.etcd_password,
                    ca_cert=self.etcd_ca_cert if self.etcd_ca_cert else None
                )
            else:
                # 无认证
                self._etcd_client = etcd3.client(
                    host=host,
                    port=port,
                    ca_cert=self.etcd_ca_cert if self.etcd_ca_cert else None
                )
                
            logger.info(f"成功连接到Etcd服务器: {host}:{port}")
            
        except Exception as e:
            logger.error(f"连接Etcd服务器失败: {str(e)}")
            self._etcd_client = None
    
    def _start_heartbeat(self):
        """启动心跳线程"""
        if self._heartbeat_thread is not None and self._heartbeat_thread.is_alive():
            logger.warning("心跳线程已启动")
            return
            
        self._stop_event.clear()
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        logger.debug("心跳线程已启动")
    
    def _stop_heartbeat(self):
        """停止心跳线程"""
        if self._heartbeat_thread is None or not self._heartbeat_thread.is_alive():
            logger.warning("心跳线程未启动")
            return
            
        self._stop_event.set()
        self._heartbeat_thread.join(timeout=5.0)
        logger.debug("心跳线程已停止")
    
    def _heartbeat_loop(self):
        """心跳循环"""
        try:
            logger.info(f"开始心跳维护服务: {self.service_id}")
            
            while not self._stop_event.is_set():
                try:
                    # 续约
                    if self._lease_id:
                        self._etcd_client.refresh_lease(self._lease_id)
                        logger.debug(f"已续约租约: {self._lease_id}")
                    
                    # 等待下一次心跳
                    self._stop_event.wait(max(1, self.lease_ttl // 3))  # 租约时间的1/3
                    
                except Exception as e:
                    logger.error(f"租约续约发生错误: {str(e)}")
                    self._stop_event.wait(5)  # 发生错误时，等待5秒后重试
                    
        except Exception as e:
            logger.error(f"心跳线程异常退出: {str(e)}")
    
    def _get_host_ip(self) -> str:
        """获取主机IP地址"""
        try:
            # 尝试获取非回环IP地址
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # 此方法不需要真正的连接
                s.connect(('10.255.255.255', 1))
                ip = s.getsockname()[0]
            return ip
        except Exception:
            # 如果失败，使用默认回环地址
            return '127.0.0.1'

class ServiceRegistryFactory:
    """服务注册工厂，用于创建不同类型的服务注册器"""
    
    @staticmethod
    def create(registry_type: str, config: Dict) -> Any:
        """
        创建服务注册器
        
        Args:
            registry_type: 注册器类型，'consul'或'etcd'
            config: 配置字典
            
        Returns:
            服务注册器实例
        """
        if registry_type.lower() == 'consul':
            return ConsulServiceRegistry(config)
        elif registry_type.lower() == 'etcd':
            return EtcdServiceRegistry(config)
        else:
            logger.error(f"不支持的服务注册器类型: {registry_type}")
            return None 