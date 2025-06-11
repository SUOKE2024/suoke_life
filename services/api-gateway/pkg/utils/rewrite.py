"""
rewrite - 索克生活项目模块
"""

from internal.model.config import RouteConfig
from typing import Dict, List, Optional, Pattern
import logging
import re

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
路径重写工具，用于根据配置的规则重写请求路径
"""




logger = logging.getLogger(__name__)


class PathRewriter:
    """路径重写器，用于重写请求路径"""

    def __init__(self) -> None:
"""初始化路径重写器"""
self.rewrite_rules: Dict[str, Dict[Pattern, str]] = {}

    def add_route_rule(self, route: RouteConfig) -> None:
"""
添加路由重写规则

Args:
            route: 路由配置
"""
if not route.rewrite_path:
            return

# 如果是第一个规则，初始化字典
if route.service not in self.rewrite_rules:
            self.rewrite_rules[route.service] = {}

# 检查重写路径中是否有正则表达式捕获组
# 格式例如: "^ / api / users / ([0 - 9] + )( / . * )?$" = > " / users / $1$2"
rewrite_parts = route.rewrite_path.split(' = >')
if len(rewrite_parts) ! = 2:
            logger.warning(f"无效的重写规则格式: {route.rewrite_path}, 将被忽略")
            return

pattern_str, target_template = [p.strip() for p in rewrite_parts]

try:
            # 编译正则表达式
            pattern = re.compile(pattern_str)

            # 添加规则
            self.rewrite_rules[route.service][pattern] = target_template
            logger.debug(f"为服务 {route.service} 添加路径重写规则: '{pattern_str}' = > '{target_template}'")
except re.error as e:
            logger.error(f"路径重写规则正则表达式编译错误: {e}, 规则: {pattern_str}")

    def rewrite_path(self, service: str, original_path: str) -> str:
"""
重写路径

Args:
            service: 服务名称
            original_path: 原始路径

Returns:
            str: 重写后的路径
"""
# 如果服务没有注册任何重写规则，直接返回原始路径
if service not in self.rewrite_rules:
            return original_path

# 尝试应用每个重写规则
for pattern, template in self.rewrite_rules[service].items():
            match = pattern.search(original_path)
            if match:
                # 如果匹配，替换捕获组
                try:
                    # 替换模板中的捕获组引用 ($1, $2, ...)
                    result = re.sub(r'\$(\d + )', lambda m: match.group(int(m.group(1))) or '', template)
                    logger.debug(f"路径重写: '{original_path}' = > '{result}'")
                    return result
                except IndexError as e:
                    logger.error(f"路径重写捕获组替换错误: {e}, 路径: {original_path}, 模板: {template}")

# 如果没有匹配的规则，返回原始路径
return original_path

    def register_routes(self, routes: List[RouteConfig]) -> None:
"""
注册多个路由配置

Args:
            routes: 路由配置列表
"""
for route in routes:
            self.add_route_rule(route)


# 辅助函数：根据路由配置创建路径重写器
def create_path_rewriter(routes: List[RouteConfig]) -> PathRewriter:
    """
    创建路径重写器

    Args:
routes: 路由配置列表

    Returns:
PathRewriter: 路径重写器
    """
    rewriter = PathRewriter()
    rewriter.register_routes(routes)
    return rewriter