# 知识图谱服务从Node.js到Go的迁移指南

本目录包含将知识图谱服务从Node.js迁移到Go过程中所需的工具和脚本。

## 迁移状态

* [x] 领域模型迁移
* [x] 存储库接口迁移
* [x] API接口定义迁移 
* [x] 数据库访问层迁移
* [x] 导入工具迁移
* [x] API服务器实现
* [x] Kubernetes配置适配
* [x] Dockerfile更新
* [ ] 完全移除Node.js代码

## 清理脚本

在完成Go实现并验证其功能后，可以使用本目录中的脚本来清理项目中不再需要的Node.js代码。

### cleanup-nodejs.sh

这个脚本会执行以下操作：

1. 备份所有Node.js相关文件和目录到`node-backup-<timestamp>`目录
2. 用Go版本的Dockerfile替换现有版本
3. 删除Node.js相关文件和目录（包括`package.json`、`tsconfig.json`和`src`目录等）

#### 使用方法

```bash
# 在项目根目录下运行
cd /path/to/suoke_life
./services/knowledge-graph-service/clean-scripts/cleanup-nodejs.sh
```

⚠️ **注意事项**:

- 运行脚本前，确保已完成Go版本的测试，并验证其功能正常
- 虽然脚本会创建备份，但建议在运行前手动备份重要文件
- 脚本必须在项目根目录下运行
- 清理后，立即测试Go版本服务，确保一切正常

## 迁移检查清单

在完全清除Node.js代码前，请检查以下项目：

- [ ] Go服务成功构建和运行
- [ ] API端点能够正确响应
- [ ] 知识图谱节点和关系操作正常
- [ ] 导入工具能够成功导入数据
- [ ] Kubernetes部署配置更新
- [ ] Helm图表更新
- [ ] CI/CD流程更新为Go构建流程
- [ ] 创建Go版本API文档 