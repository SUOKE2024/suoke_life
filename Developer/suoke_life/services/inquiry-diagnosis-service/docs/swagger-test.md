# API测试指南

本文档提供使用Swagger UI测试索克生活问诊诊断服务API的步骤和示例。

## 准备工作

1. 启动服务
   ```bash
   npm run dev
   ```

2. 访问Swagger UI
   ```
   http://localhost:3007/api-docs
   ```

## 授权设置

某些API需要授权才能访问。在Swagger UI中设置授权的步骤：

1. 点击右上角的"Authorize"按钮
2. 在显示的对话框中设置授权信息：
   - Bearer Token: 输入`Bearer your_jwt_token`
   - API Key: 输入API密钥

## 常用测试流程

### 1. 健康检查API

首先，验证服务是否正常运行：

1. 在"系统"标签下找到`GET /api/health`端点
2. 点击"Try it out"按钮
3. 点击"Execute"按钮
4. 应该看到200状态码和包含服务状态的JSON响应

### 2. 创建问诊会话

1. 在"问诊"标签下找到`POST /api/inquiry/sessions`端点
2. 点击"Try it out"按钮
3. 输入请求体，例如：
   ```json
   {
     "userId": "user123",
     "patientInfo": {
       "name": "测试用户",
       "age": 35,
       "gender": "male"
     },
     "preferences": {
       "language": "zh-CN",
       "responseLength": "detailed"
     }
   }
   ```
4. 点击"Execute"按钮
5. 保存响应中的`sessionId`，后续测试需要使用

### 3. 提交问诊请求

1. 在"问诊"标签下找到`POST /api/inquiry/sessions/{sessionId}/inquiries`端点
2. 点击"Try it out"按钮
3. 输入上一步获取的`sessionId`
4. 输入请求体，例如：
   ```json
   {
     "content": "最近睡眠不好，容易醒，醒后难以入睡，白天精神不振。"
   }
   ```
5. 点击"Execute"按钮
6. 查看响应，应该包含AI助手的回复和可能提取的症状

### 4. 生成中医辨证诊断

1. 在"诊断"标签下找到`POST /api/diagnosis/tcm-pattern`端点
2. 点击"Try it out"按钮
3. 输入请求体，例如：
   ```json
   {
     "sessionId": "之前保存的sessionId",
     "userId": "user123",
     "symptoms": [
       "失眠",
       "易醒",
       "难以入睡",
       "精神不振"
     ]
   }
   ```
4. 点击"Execute"按钮
5. 检查响应中的辨证结果和调理建议

### 5. 查看诊断历史

1. 在"诊断"标签下找到`GET /api/diagnosis/history/{userId}`端点
2. 点击"Try it out"按钮
3. 输入`userId`为"user123"
4. 设置`limit`为10，`offset`为0
5. 点击"Execute"按钮
6. 查看用户的诊断历史记录

## 测试四诊协调API

四诊协调API通常由其他服务调用，但我们可以使用Swagger UI进行模拟测试：

1. 在"四诊协调"标签下找到`POST /api/coordinator/webhook/diagnosis`端点
2. 点击"Try it out"按钮
3. 确保已设置API密钥授权
4. 输入请求体，例如：
   ```json
   {
     "sessionId": "之前保存的sessionId",
     "diagnosisId": "diag123",
     "diagnosisType": "integrated",
     "diagnosisData": {
       "patterns": ["心脾两虚"],
       "recommendations": ["养心安神，健脾益气"]
     }
   }
   ```
5. 点击"Execute"按钮
6. 应该看到200状态码和成功响应

## 故障排除

如果API测试失败，请检查：

1. 服务是否正常运行（使用健康检查API）
2. 授权是否正确设置
3. 请求参数是否符合要求
4. 查看服务日志了解详细错误信息

## 常见问题

1. **401 Unauthorized**：检查授权设置是否正确
2. **400 Bad Request**：检查请求参数是否符合要求
3. **404 Not Found**：检查URL和资源ID是否正确
4. **500 Internal Server Error**：服务器内部错误，查看日志获取详细信息