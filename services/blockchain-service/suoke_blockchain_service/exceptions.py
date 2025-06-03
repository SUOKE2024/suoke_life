"""
自定义异常类

定义区块链服务相关的异常类型。
"""

class BlockchainServiceError(Exception):
    """区块链服务基础异常"""
    pass

class ValidationError(BlockchainServiceError):
    """验证错误"""
    pass

class NotFoundError(BlockchainServiceError):
    """资源不存在错误"""
    pass

class PermissionError(BlockchainServiceError):
    """权限错误"""
    pass

class IntegrationError(BlockchainServiceError):
    """集成错误"""
    pass

class ContractError(BlockchainServiceError):
    """智能合约错误"""
    pass

class TransactionError(BlockchainServiceError):
    """交易错误"""
    pass

class EncryptionError(BlockchainServiceError):
    """加密错误"""
    pass

class ZKProofError(BlockchainServiceError):
    """零知识证明错误"""
    pass

class IPFSError(BlockchainServiceError):
    """IPFS错误"""
    pass 