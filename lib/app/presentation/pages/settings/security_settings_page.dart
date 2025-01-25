import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/settings/security_settings_controller.dart';

class SecuritySettingsPage extends StatelessWidget {
  const SecuritySettingsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('安全设置'),
      ),
      body: ListView(
        children: [
          // 账号安全
          const ListTile(
            title: Text('账号安全'),
            dense: true,
            enabled: false,
          ),
          ListTile(
            title: const Text('修改密码'),
            trailing: const Icon(Icons.chevron_right),
            onTap: controller.changePassword,
          ),
          ListTile(
            title: const Text('手机号验证'),
            subtitle: Obx(() => Text(controller.phoneVerified.value ? '已验证' : '未验证')),
            trailing: const Icon(Icons.chevron_right),
            onTap: controller.verifyPhone,
          ),
          ListTile(
            title: const Text('邮箱���证'),
            subtitle: Obx(() => Text(controller.emailVerified.value ? '已验证' : '未验证')),
            trailing: const Icon(Icons.chevron_right),
            onTap: controller.verifyEmail,
          ),

          const Divider(),

          // 登录安全
          const ListTile(
            title: Text('登录安全'),
            dense: true,
            enabled: false,
          ),
          ListTile(
            title: const Text('生物识别'),
            trailing: Obx(() => Switch(
              value: controller.biometricEnabled.value,
              onChanged: controller.toggleBiometric,
            )),
          ),
          ListTile(
            title: const Text('两步验证'),
            trailing: Obx(() => Switch(
              value: controller.twoFactorEnabled.value,
              onChanged: controller.toggleTwoFactor,
            )),
          ),
          ListTile(
            title: const Text('登录设备管理'),
            trailing: const Icon(Icons.chevron_right),
            onTap: controller.manageDevices,
          ),
        ],
      ),
    );
  }
} 