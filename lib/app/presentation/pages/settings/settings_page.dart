import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/settings/settings_controller.dart';

class SettingsPage extends GetView<SettingsController> {
  const SettingsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('设置'),
      ),
      body: ListView(
        children: [
          // 通用设置
          const ListTile(
            title: Text('通用'),
            dense: true,
            visualDensity: VisualDensity.compact,
            enabled: false,
          ),
          ListTile(
            title: const Text('语言'),
            trailing: Obx(() => Text(controller.currentLanguage)),
            onTap: controller.changeLanguage,
          ),
          ListTile(
            title: const Text('主题'),
            trailing: Obx(() => Text(controller.currentTheme)),
            onTap: controller.changeTheme,
          ),
          ListTile(
            title: const Text('字体大小'),
            trailing: Obx(() => Text(controller.fontSize.value)),
            onTap: controller.changeFontSize,
          ),

          const Divider(),

          // 隐私设置
          const ListTile(
            title: Text('隐私'),
            dense: true,
            visualDensity: VisualDensity.compact,
            enabled: false,
          ),
          ListTile(
            title: const Text('通知'),
            trailing: Obx(() => Switch(
              value: controller.notificationsEnabled.value,
              onChanged: controller.toggleNotifications,
            )),
          ),
          ListTile(
            title: const Text('生物识别'),
            trailing: Obx(() => Switch(
              value: controller.biometricEnabled.value,
              onChanged: controller.toggleBiometric,
            )),
          ),

          const Divider(),

          // 其他设置
          const ListTile(
            title: Text('其他'),
            dense: true,
            visualDensity: VisualDensity.compact,
            enabled: false,
          ),
          ListTile(
            title: const Text('清除缓存'),
            trailing: Obx(() => Text(controller.cacheSize.value)),
            onTap: controller.clearCache,
          ),
          ListTile(
            title: const Text('关于'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => Get.toNamed('/settings/about'),
          ),
        ],
      ),
    );
  }
} 