
"""
算诊服务自定义异常类
"""


class CalculationError(Exception):
    """算诊计算基础异常"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class InvalidBirthInfoError(CalculationError):
    """无效出生信息异常"""
    
    def __init__(self, message: str = "出生信息无效"):
        super().__init__(message, "INVALID_BIRTH_INFO")


class InvalidTimeError(CalculationError):
    """无效时间异常"""
    
    def __init__(self, message: str = "时间格式无效"):
        super().__init__(message, "INVALID_TIME")


class AlgorithmError(CalculationError):
    """算法计算异常"""
    
    def __init__(self, algorithm_name: str, message: str = "算法计算失败"):
        self.algorithm_name = algorithm_name
        super().__init__(f"{algorithm_name}: {message}", "ALGORITHM_ERROR")


class DataNotFoundError(CalculationError):
    """数据未找到异常"""
    
    def __init__(self, data_type: str, message: str = "数据未找到"):
        self.data_type = data_type
        super().__init__(f"{data_type}: {message}", "DATA_NOT_FOUND")


class ConfigurationError(CalculationError):
    """配置错误异常"""
    
    def __init__(self, message: str = "配置错误"):
        super().__init__(message, "CONFIGURATION_ERROR")


class ValidationError(CalculationError):
    """数据验证异常"""
    
    def __init__(self, field: str, message: str = "数据验证失败"):
        self.field = field
        super().__init__(f"{field}: {message}", "VALIDATION_ERROR") 