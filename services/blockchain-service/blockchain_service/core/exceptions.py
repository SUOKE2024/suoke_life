"""
异常定义模块

定义区块链服务中使用的所有自定义异常类。
"""

from typing import Any


class BlockchainServiceError(Exception):
    """区块链服务基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class ConfigurationError(BlockchainServiceError):
    """配置错误"""
    pass


class ValidationError(BlockchainServiceError):
    """数据验证错误"""
    pass


class NetworkError(BlockchainServiceError):
    """网络连接错误"""
    pass


class StorageError(BlockchainServiceError):
    """存储操作错误"""
    pass


class ContractError(BlockchainServiceError):
    """智能合约错误"""
    pass


class CryptographyError(BlockchainServiceError):
    """加密操作错误"""
    pass


class ZKProofError(BlockchainServiceError):
    """零知识证明错误"""
    pass


class IPFSError(BlockchainServiceError):
    """IPFS操作错误"""
    pass
