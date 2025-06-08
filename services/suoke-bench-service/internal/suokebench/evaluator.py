from typing import Dict, List, Any, Optional, Union

"""
evaluator - 索克生活项目模块
"""


# 索克生活 - 中医五诊评估任务配置

# 五诊评估任务
TCM_5D_EVALUATION = {
    'name': '中医五诊综合评估',
    'description': '评估智能体对中医五诊（望、闻、问、切、算）的理解和应用能力',
    'data_path': 'data / tcm - 5d / ',
    'metrics': ['accuracy', 'precision', 'recall', 'f1_score'],
    'categories': ['望诊', '闻诊', '问诊', '切诊', '算诊']
}