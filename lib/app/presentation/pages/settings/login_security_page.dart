import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/login_security_controller.dart';

class LoginSecurityPage extends BasePage<LoginSecurityController> {
  const LoginSecurityPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('登录安全设置'),
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // 生物识别登录
        Card(
          child: Column(
            children: [
              ListTile(
                title: const Text('生物识别登录'),
                subtitle: const Text('使用指纹或面容ID快速登录'),
                trailing: Obx(() => Switch(
                  value: controller.biometricEnabled.value,
                  onChanged: controller.toggleBiometric,
                )),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // 登录保护
        Card(
          child: Column(
            children: [
              ListTile(
                title: const Text('登录保护'),
                subtitle: const Text('异常登录行为检测和防护'),
              ),
              const Divider(height: 1),
              ListTile(
                title: const Text('登录验证'),
                subtitle: const Text('异地登录时需要验证'),
                trailing: Obx(() => Switch(
                  value: controller.loginVerificationEnabled.value,
                  onChanged: controller.toggleLoginVerification,
                )),
              ),
              const Divider(height: 1),
              ListTile(
                title: const Text('登录通知'),
                subtitle: const Text('新设备登录时通知'),
                trailing: Obx(() => Switch(
                  value: controller.loginNotificationEnabled.value,
                  onChanged: controller.toggleLoginNotification,
                )),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // 密码安全
        Card(
          child: Column(
            children: [
              ListTile(
                title: const Text('密码安全'),
                subtitle: const Text('密码相关安全设置'),
              ),
              const Divider(height: 1),
              ListTile(
                title: const Text('修改密码'),
                trailing: const Icon(Icons.chevron_right),
                onTap: controller.showChangePasswordDialog,
              ),
              const Divider(height: 1),
              ListTile(
                title: const Text('定期修改密码提醒'),
                subtitle: const Text('每90天提醒修改密码'),
                trailing: Obx(() => Switch(
                  value: controller.passwordChangeReminder.value,
                  onChanged: controller.togglePasswordChangeReminder,
                )),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // 设备管理
        Card(
          child: Column(
            children: [
              ListTile(
                title: const Text('设备管理'),
                subtitle: const Text('管理已登录的设备'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.pushNamed('/settings/devices'),
              ),
              const Divider(height: 1),
              ListTile(
                title: const Text('登录历史'),
                subtitle: const Text('查看登录记录'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.pushNamed('/settings/login-history'),
              ),
            ],
          ),
        ),
      ],
    );
  }
} 