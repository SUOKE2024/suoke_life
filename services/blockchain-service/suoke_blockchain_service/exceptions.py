"""
区块链服务异常定义
"""

from typing import Any


class BlockchainServiceError(Exception):
    """区块链服务基础异常"""

    def __init__(self, message: str, error_code: str = "BLOCKCHAIN_ERROR"):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self):
        return f"[{self.error_code}] {self.message}"


class ValidationError(BlockchainServiceError):
    """验证错误"""

    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class NotFoundError(BlockchainServiceError):
    """资源未找到错误"""

    def __init__(self, message: str):
        super().__init__(message, "NOT_FOUND_ERROR")


class IPFSError(BlockchainServiceError):
    """IPFS相关错误"""

    def __init__(self, message: str):
        super().__init__(message, "IPFS_ERROR")


def validate_required_fields(data: dict[str, Any], required_fields: list) -> None:
    """验证必需字段"""
    for field in required_fields:
        if field not in data or data[field] is None:
            raise ValidationError(f"缺少必需字段: {field}")


def main() -> None:
    """主函数 - 自动生成的最小可用版本"""
    pass


if __name__ == "__main__":
    main()
