import 'base/legal_document_controller.dart';

class PrivacyPolicyController extends LegalDocumentController {
  @override
  String get title => '索克生活隐私政策';

  @override
  Future<String> loadDocument() async {
    // TODO: 从服务器或本地加载隐私政策内容
    await Future.delayed(const Duration(seconds: 1));
    return '''
# 索克生活隐私政策

我们非常重视您的隐私保护。本政策说明我们如何收集、使用和保护您的个人信息。

## 1. 信息收集

### 1.1 主动提供的信息

- 账号信息（用户名、密码）
- 个人资料（昵称、头像）
- 联系方式（手机号、邮箱）

### 1.2 自动收集的信息

- 设备信息
- 位置信息
- 使用数据

## 2. 信息使用

我们使用收集的信息用于：

- 提供和改进服务
- 个性化用户体验
- 安全防护
- 数据分析

## 3. 信息保护

### 3.1 数据安全

- 加密存储
- 访问控制
- 安全审计

### 3.2 数据共享

除以下情况外，我们不会共享您的个人信息：

- 获得您的明确同意
- 法律法规要求
- 保护用户权益

## 4. 用户权利

您有权：

- 访问个人信息
- 更正错误信息
- 删除账号
- 导出数据

## 5. Cookie 使用

我们使用 Cookie 来：

- 保持登录状态
- 记住偏好设置
- 提供个性化服务

## 6. 儿童隐私

我们不会故意收集 14 岁以下儿童的个人信息。

## 7. 政策更新

我们可能会更新本隐私政策，更新后将在应用内通知您。

## 8. 联系我们

隐私问题联系方式：

- 邮箱：privacy@suoke.life
- 电话：400-123-4567

*最后更新：2024年3月21日*
''';
  }
} 