#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback

# 添加项目路径
sys.path.append('.')

try:
    from internal.agent.model_config_manager import get_model_config_manager
    print('✓ 配置管理器导入成功')
except Exception as e:
    print(f'❌ 配置管理器导入失败: {e}')
    traceback.print_exc()