import 'base/legal_document_controller.dart';

class UserAgreementController extends LegalDocumentController {
  @override
  String get title => '索克生活用户协议';

  @override
  Future<String> loadDocument() async {
    // TODO: 从服务器或本地加载用户协议内容
    await Future.delayed(const Duration(seconds: 1));
    return '''
# 索克生活用户协议

欢迎使用索克生活！本协议是您与索克生活（以下简称"我们"）之间的法律协议，请您仔细阅读。

## 1. 服务内容

索克生活是一款提供生活服务和AI助手功能的应用程序。我们提供以下服务：

- 智能对话
- 生活记录
- 健康管理
- 数据同步

## 2. 用户权利和义务

### 2.1 账号注册

您承诺：

- 提供真实、准确、完整的个人资料
- 保护账号安全，不与他人分享
- 遵守相关法律法规

### 2.2 使用规范

您同意：

- 不发布违法、违规内容
- 尊重他人知识产权
- 维护良好的社区环境

## 3. 隐私保护

我们重视您的隐私保护，具体请参考[隐私政策](#privacy)。

## 4. 免责声明

- AI助手提供的建议仅供参考
- 不对第三方链接负责
- 不承担因不可抗力导致的损失

## 5. 协议修改

我们保留随时修改本协议的权利，修改后的协议将在应用内公布。

## 6. 联系我们

如有任何问题，请通过以下方式联系我们：

- 邮箱：support@suoke.life
- 电话：400-123-4567

*最后更新：2024年3月21日*
''';
  }
} 