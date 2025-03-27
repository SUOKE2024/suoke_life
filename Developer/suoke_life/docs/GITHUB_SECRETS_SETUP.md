# GitHub Secrets 配置指南

## 必需的Secrets

为了确保CI/CD流程正常运行，需要在GitHub仓库中配置以下Secrets：

### 阿里云容器镜像服务认证
- `ALIYUN_REGISTRY_USERNAME`: 阿里云容器镜像服务登录用户名
- `ALIYUN_REGISTRY_PASSWORD`: 阿里云容器镜像服务登录密码

### 阿里云访问凭证
- `ALIYUN_ACCESS_KEY_ID`: 阿里云访问密钥ID
- `ALIYUN_ACCESS_KEY_SECRET`: 阿里云访问密钥密码

## 配置步骤

1. 访问GitHub仓库的Settings页面
2. 在左侧导航栏中选择"Secrets and variables" -> "Actions"
3. 点击"New repository secret"按钮
4. 添加上述每个Secret：
   - Name: 使用上述Secret名称
   - Value: 填入对应的值
   - 点击"Add secret"保存

## 验证配置

配置完成后，可以：

1. 手动触发"检查部署状态"工作流
2. 检查工作流运行日志，确认没有认证相关的错误
3. 确认镜像拉取和推送操作正常进行

## 安全提示

- 定期轮换这些凭证以提高安全性
- 确保这些凭证具有最小必要权限
- 不要在代码或日志中暴露这些凭证
- 在本地开发环境使用单独的测试凭证

## 故障排除

如果遇到认证相关的错误：
1. 确认所有secrets都已正确设置
2. 检查凭证是否过期
3. 验证账号是否有足够的权限
4. 查看GitHub Actions日志中的具体错误信息 