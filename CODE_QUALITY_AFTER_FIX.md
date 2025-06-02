# 🔍 代码质量检查报告

**检查时间**: 2025年 6月 2日 星期一 18时14分04秒 CST
**项目路径**: .

## 📊 统计信息

- Python文件检查: 4298 个
- JavaScript/TypeScript文件检查: 1268 个
- 未使用导入: 0 个
- 重复代码行: 15474 个
- 高复杂度函数: 1857 个
- TODO注释: 3760 个
- Console.log语句: 2018 个

## 🚨 发现的问题


### Duplicate Lines

- **tests/test_integration.py**
  - 重复项: 7 个
- **scripts/microservices_manager.py**
  - 重复项: 1 个
- **scripts/migrate_to_postgresql.py**
  - 重复项: 1 个
- **scripts/microservices_completion_tool.py**
  - 重复项: 1 个
- **services/message-bus/blockchain_integration.py**
  - 重复项: 6 个

... 还有 2657 个类似问题

### High Complexity

- **scripts/microservices_manager.py**
  - 函数: main, 复杂度: 12
- **scripts/microservices_completion_tool.py**
  - 函数: evaluate_service_completion, 复杂度: 13
- **services/corn-maze-service/pkg/utils/rate_limiter.py**
  - 函数: is_allowed, 复杂度: 12
- **services/corn-maze-service/internal/repository/maze_repository.py**
  - 函数: search_mazes, 复杂度: 13
- **services/corn-maze-service/internal/repository/template_repository.py**
  - 函数: _generate_template_cells, 复杂度: 12

... 还有 1852 个类似问题

### Todos

- **src/services/zkp_utils.py**
  - TODO数量: 3
- **services/corn-maze-service/tests/conftest.py**
  - TODO数量: 1
- **services/corn-maze-service/corn_maze_service/internal/delivery/grpc.py**
  - TODO数量: 1
- **services/corn-maze-service/corn_maze_service/internal/delivery/http.py**
  - TODO数量: 4
- **services/corn-maze-service/corn_maze_service/cmd/server/main.py**
  - TODO数量: 1

... 还有 906 个类似问题

### Syntax Errors

- **services/suoke-bench-service/internal/suokebench/evaluator.py**
- **services/med-knowledge/app/services/knowledge_service.py**
- **services/accessibility-service/accessibility_service/internal/model/health_data.py**
- **services/rag-service/internal/service/intelligent_tcm_constitution_engine.py**
- **services/rag-service/cmd/server/main.py**

... 还有 1 个类似问题

### Console Logs

- **cursor-voice-extension/test-extension.js**
  - Console.log数量: 16
- **cursor-voice-extension/test-keybindings.js**
  - Console.log数量: 24
- **scripts/manual-syntax-fix.js**
  - Console.log数量: 10
- **scripts/final-bug-fix.js**
  - Console.log数量: 9
- **scripts/comment-format-fix.js**
  - Console.log数量: 9

... 还有 121 个类似问题

### Js Unused Imports

- **scripts/test/test-frontend-navigation.js**
- **scripts/test/test-frontend-navigation.js**
- **scripts/test/test-frontend-navigation.js**
- **src/config/onnxConfig.ts**
- **src/utils/modelQuantization.ts**

... 还有 343 个类似问题

### Duplicate Python Deps

- **requirements.txt**
  - 重复项: 1 个


## 🎯 建议的清理操作

1. **清理未使用的导入**: 删除 0 个未使用的导入
2. **重构重复代码**: 提取 15474 处重复代码为函数
3. **降低复杂度**: 重构 1857 个高复杂度函数
4. **清理调试代码**: 删除 2018 个console.log语句
5. **处理TODO**: 完成或删除 3760 个TODO注释

## 🔧 自动修复建议

```bash
# 使用工具自动修复
npm run lint:fix  # 修复JavaScript/TypeScript问题
autopep8 --in-place --recursive .  # 修复Python格式问题
isort .  # 排序Python导入
```

## 📈 代码质量评分

总体评分: 20/100

