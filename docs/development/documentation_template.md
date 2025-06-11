# API文档模板

## 模块文档规范

### 模块级docstring
```python
"""
模块简短描述

详细描述模块的功能和用途。

Examples:
    基本用法示例:
    
    >>> from module import function
    >>> result = function()

Note:
    特殊说明或注意事项

Todo:
    * 待完成的功能
    * 需要改进的地方
"""
```

### 类文档规范
```python
class ExampleClass:
    """
    类的简短描述
    
    详细描述类的功能、用途和设计意图。
    
    Attributes:
        attr1 (str): 属性1的描述
        attr2 (int): 属性2的描述
    
    Examples:
        >>> obj = ExampleClass()
        >>> obj.method()
    """
```

### 函数文档规范
```python
def example_function(param1: str, param2: int = 0) -> bool:
    """
    函数的简短描述
    
    详细描述函数的功能和行为。
    
    Args:
        param1 (str): 参数1的描述
        param2 (int, optional): 参数2的描述. Defaults to 0.
    
    Returns:
        bool: 返回值的描述
    
    Raises:
        ValueError: 什么情况下抛出此异常
        TypeError: 什么情况下抛出此异常
    
    Examples:
        >>> result = example_function("test", 5)
        >>> print(result)
        True
    """
```

## 文档编写最佳实践

1. **简洁明了**: 第一行应该是简短的功能描述
2. **详细说明**: 提供足够的细节帮助用户理解
3. **参数说明**: 清楚说明每个参数的类型和用途
4. **返回值**: 说明返回值的类型和含义
5. **异常处理**: 列出可能抛出的异常
6. **示例代码**: 提供实际的使用示例
7. **类型注解**: 使用类型注解提高代码可读性

## 文档生成工具

使用以下命令生成API文档:
```bash
python scripts/generate_api_docs.py
```
