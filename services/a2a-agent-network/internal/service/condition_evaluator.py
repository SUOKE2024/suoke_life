#!/usr/bin/env python3
"""
条件评估器
Condition Evaluator
"""

import re
from typing import Any, Dict

from ..model.workflow import ConditionOperator, ConditionRule


class ConditionEvaluator:
    """条件评估器类"""

    def __init__(self):
        """初始化条件评估器"""
        self._operators = {
            ConditionOperator.EQUALS: self._equals,
            ConditionOperator.NOT_EQUALS: self._not_equals,
            ConditionOperator.GREATER_THAN: self._greater_than,
            ConditionOperator.GREATER_EQUAL: self._greater_equal,
            ConditionOperator.LESS_THAN: self._less_than,
            ConditionOperator.LESS_EQUAL: self._less_equal,
            ConditionOperator.CONTAINS: self._contains,
            ConditionOperator.NOT_CONTAINS: self._not_contains,
            ConditionOperator.IN: self._in,
            ConditionOperator.NOT_IN: self._not_in,
            ConditionOperator.EXISTS: self._exists,
            ConditionOperator.NOT_EXISTS: self._not_exists,
        }

    def evaluate(self, condition: ConditionRule, context: Dict[str, Any]) -> bool:
        """
        评估条件规则

        Args:
            condition: 条件规则
            context: 执行上下文

        Returns:
            bool: 条件评估结果
        """
        try:
            # 获取字段值
            field_value = self._get_field_value(condition.field, context)
            
            # 获取操作符函数
            operator_func = self._operators.get(condition.operator)
            if not operator_func:
                raise ValueError(f"不支持的操作符: {condition.operator}")

            # 执行条件评估
            result = operator_func(field_value, condition.value)
            
            return result

        except Exception as e:
            # 条件评估失败时返回 False
            print(f"条件评估失败: {e}")
            return False

    def _get_field_value(self, field_path: str, context: Dict[str, Any]) -> Any:
        """
        从上下文中获取字段值

        Args:
            field_path: 字段路径，如 'context.user.age'
            context: 执行上下文

        Returns:
            Any: 字段值
        """
        try:
            # 分割字段路径
            parts = field_path.split('.')
            value = context

            # 逐级获取值
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                elif hasattr(value, part):
                    value = getattr(value, part)
                else:
                    return None

            return value

        except Exception:
            return None

    def _equals(self, field_value: Any, compare_value: Any) -> bool:
        """等于操作"""
        return field_value == compare_value

    def _not_equals(self, field_value: Any, compare_value: Any) -> bool:
        """不等于操作"""
        return field_value != compare_value

    def _greater_than(self, field_value: Any, compare_value: Any) -> bool:
        """大于操作"""
        try:
            return float(field_value) > float(compare_value)
        except (TypeError, ValueError):
            return False

    def _greater_equal(self, field_value: Any, compare_value: Any) -> bool:
        """大于等于操作"""
        try:
            return float(field_value) >= float(compare_value)
        except (TypeError, ValueError):
            return False

    def _less_than(self, field_value: Any, compare_value: Any) -> bool:
        """小于操作"""
        try:
            return float(field_value) < float(compare_value)
        except (TypeError, ValueError):
            return False

    def _less_equal(self, field_value: Any, compare_value: Any) -> bool:
        """小于等于操作"""
        try:
            return float(field_value) <= float(compare_value)
        except (TypeError, ValueError):
            return False

    def _contains(self, field_value: Any, compare_value: Any) -> bool:
        """包含操作"""
        try:
            if isinstance(field_value, (list, tuple)):
                return compare_value in field_value
            elif isinstance(field_value, str):
                return str(compare_value) in field_value
            elif isinstance(field_value, dict):
                return compare_value in field_value.values()
            return False
        except Exception:
            return False

    def _not_contains(self, field_value: Any, compare_value: Any) -> bool:
        """不包含操作"""
        return not self._contains(field_value, compare_value)

    def _in(self, field_value: Any, compare_value: Any) -> bool:
        """在列表中操作"""
        try:
            if isinstance(compare_value, (list, tuple)):
                return field_value in compare_value
            return False
        except Exception:
            return False

    def _not_in(self, field_value: Any, compare_value: Any) -> bool:
        """不在列表中操作"""
        return not self._in(field_value, compare_value)

    def _exists(self, field_value: Any, compare_value: Any) -> bool:
        """存在操作"""
        return field_value is not None

    def _not_exists(self, field_value: Any, compare_value: Any) -> bool:
        """不存在操作"""
        return field_value is None

    def evaluate_expression(self, expression: str, context: Dict[str, Any]) -> bool:
        """
        评估复杂表达式

        Args:
            expression: 表达式字符串，如 "age > 18 AND status == 'active'"
            context: 执行上下文

        Returns:
            bool: 表达式评估结果
        """
        try:
            # 简单的表达式解析器
            # 支持 AND, OR, NOT 逻辑操作符
            
            # 替换变量
            processed_expr = self._replace_variables(expression, context)
            
            # 安全评估表达式
            # 注意：这里使用 eval 有安全风险，生产环境应该使用更安全的表达式解析器
            result = eval(processed_expr, {"__builtins__": {}}, {})
            
            return bool(result)

        except Exception as e:
            print(f"表达式评估失败: {e}")
            return False

    def _replace_variables(self, expression: str, context: Dict[str, Any]) -> str:
        """
        替换表达式中的变量

        Args:
            expression: 原始表达式
            context: 执行上下文

        Returns:
            str: 替换后的表达式
        """
        # 查找所有变量引用（如 ${variable.path}）
        pattern = r'\$\{([^}]+)\}'
        
        def replace_var(match):
            var_path = match.group(1)
            value = self._get_field_value(var_path, context)
            
            # 根据值类型进行适当的转换
            if isinstance(value, str):
                return f"'{value}'"
            elif value is None:
                return "None"
            else:
                return str(value)

        return re.sub(pattern, replace_var, expression)


class LoopController:
    """循环控制器类"""

    def __init__(self, condition_evaluator: ConditionEvaluator):
        """初始化循环控制器"""
        self.condition_evaluator = condition_evaluator

    def should_continue_loop(
        self, 
        loop_config: "LoopConfig", 
        context: Dict[str, Any], 
        iteration: int
    ) -> bool:
        """
        判断是否应该继续循环

        Args:
            loop_config: 循环配置
            context: 执行上下文
            iteration: 当前迭代次数

        Returns:
            bool: 是否继续循环
        """
        # 检查最大迭代次数
        if iteration >= loop_config.max_iterations:
            return False

        # 根据循环类型判断
        if loop_config.type == "for":
            # for 循环由迭代次数控制
            return iteration < loop_config.max_iterations

        elif loop_config.type == "while":
            # while 循环由条件控制
            if loop_config.condition:
                return self.condition_evaluator.evaluate(loop_config.condition, context)
            return False

        elif loop_config.type == "foreach":
            # foreach 循环由集合大小控制
            if loop_config.collection_path:
                collection = self.condition_evaluator._get_field_value(
                    loop_config.collection_path, context
                )
                if isinstance(collection, (list, tuple)):
                    return iteration < len(collection)
            return False

        return False

    def prepare_loop_context(
        self, 
        loop_config: "LoopConfig", 
        context: Dict[str, Any], 
        iteration: int
    ) -> Dict[str, Any]:
        """
        准备循环上下文

        Args:
            loop_config: 循环配置
            context: 原始上下文
            iteration: 当前迭代次数

        Returns:
            Dict[str, Any]: 循环上下文
        """
        loop_context = context.copy()
        
        # 设置迭代变量
        loop_context[loop_config.iteration_variable] = iteration

        # 对于 foreach 循环，设置当前项
        if loop_config.type == "foreach" and loop_config.collection_path:
            collection = self.condition_evaluator._get_field_value(
                loop_config.collection_path, context
            )
            if isinstance(collection, (list, tuple)) and iteration < len(collection):
                loop_context["current_item"] = collection[iteration]

        return loop_context 