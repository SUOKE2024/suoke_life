
"""
test_exceptions_quick - 索克生活项目模块
"""

import sys; sys.path.insert(0, "."); from suoke_blockchain_service.exceptions import * ; print("✓ 异常模块导入成功"); error = BlockchainServiceError("Test"); print(f"✓ 基本异常: {error.error_code}"); validate_required_fields({"name": "test"}, ["name"]); print("✓ 验证函数工作正常"); print("🎉 异常处理优化验证成功!")

