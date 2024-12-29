import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/profile/settings_controller.dart';

class SettingsPage extends GetView<SettingsController> {
  const SettingsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('设置'),
      ),
      body: Obx(() => ListView(
        children: [
          // 通知设置
          ListTile(
            title: const Text('通知'),
            trailing: Switch(
              value: controller.notificationsEnabled.value,
              onChanged: controller.toggleNotifications,
            ),
          ),
          // 声音设置
          ListTile(
            title: const Text('声音'),
            trailing: Switch(
              value: controller.soundEnabled.value,
              onChanged: controller.toggleSound,
            ),
          ),
          // 语言设置
          ListTile(
            title: const Text('语言'),
            trailing: DropdownButton<String>(
              value: controller.currentLanguage.value,
              items: controller.supportedLanguages.map((lang) {
                return DropdownMenuItem(
                  value: lang,
                  child: Text(lang),
                );
              }).toList(),
              onChanged: controller.changeLanguage,
            ),
          ),
          // 主题设置
          ListTile(
            title: const Text('主题'),
            trailing: DropdownButton<String>(
              value: controller.currentTheme.value,
              items: controller.supportedThemes.map((theme) {
                return DropdownMenuItem(
                  value: theme,
                  child: Text(theme),
                );
              }).toList(),
              onChanged: controller.changeTheme,
            ),
          ),
          // 清除缓存
          ListTile(
            title: const Text('清除缓存'),
            trailing: Text(controller.cacheSize.value),
            onTap: controller.clearCache,
          ),
          // 退出登录
          ListTile(
            title: const Text('退出登录'),
            onTap: controller.logout,
          ),
        ],
      )),
    );
  }
} 