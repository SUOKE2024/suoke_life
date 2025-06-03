"""
IPFS客户端模块

提供与IPFS网络的集成功能。
"""

import aiohttp
import json
from typing import Any, Dict, Optional

from .config import settings
from .exceptions import IPFSError
from .logging import get_logger

logger = get_logger(__name__)

class IPFSClient:
    """IPFS客户端"""

    def __init__(self):
        self.base_url = settings.ipfs.node_url
        self.timeout = aiohttp.ClientTimeout(total=30)

    async def upload_data(self, data: bytes) -> str:
        """上传数据到IPFS"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # 创建表单数据
                form_data = aiohttp.FormData()
                form_data.add_field('file', data, filename='data.bin')

                # 上传到IPFS
                async with session.post(
                    f"{self.base_url}/api/v0/add",
                    data=form_data
                ) as response:
                    if response.status != 200:
                        raise IPFSError(f"IPFS上传失败: {response.status}")

                    result = await response.json()
                    ipfs_hash = result.get('Hash')

                    if not ipfs_hash:
                        raise IPFSError("IPFS返回的哈希为空")

                    logger.info("数据上传到IPFS成功", hash=ipfs_hash, size=len(data))
                    return ipfs_hash

        except Exception as e:
            logger.error("IPFS上传失败", error=str(e))
            raise IPFSError(f"IPFS上传失败: {str(e)}")

    async def get_data(self, ipfs_hash: str) -> bytes:
        """从IPFS获取数据"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/v0/cat",
                    params={'arg': ipfs_hash}
                ) as response:
                    if response.status != 200:
                        raise IPFSError(f"IPFS获取失败: {response.status}")

                    data = await response.read()
                    logger.info("从IPFS获取数据成功", hash=ipfs_hash, size=len(data))
                    return data

        except Exception as e:
            logger.error("IPFS获取失败", hash=ipfs_hash, error=str(e))
            raise IPFSError(f"IPFS获取失败: {str(e)}")

    async def pin_data(self, ipfs_hash: str) -> bool:
        """固定IPFS数据"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/v0/pin/add",
                    params={'arg': ipfs_hash}
                ) as response:
                    if response.status != 200:
                        raise IPFSError(f"IPFS固定失败: {response.status}")

                    logger.info("IPFS数据固定成功", hash=ipfs_hash)
                    return True

        except Exception as e:
            logger.error("IPFS固定失败", hash=ipfs_hash, error=str(e))
            raise IPFSError(f"IPFS固定失败: {str(e)}")

    async def get_node_info(self) -> Dict[str, Any]:
        """获取IPFS节点信息"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/v0/id"
                ) as response:
                    if response.status != 200:
                        raise IPFSError(f"获取节点信息失败: {response.status}")

                    return await response.json()

        except Exception as e:
            logger.error("获取IPFS节点信息失败", error=str(e))
            raise IPFSError(f"获取IPFS节点信息失败: {str(e)}") 