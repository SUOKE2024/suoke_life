import 'package:flutter/material.dart';
import '../../core/base/base_page.dart';
import '../../../controllers/settings_controller.dart';
import 'package:get/get.dart';
import '../../../routes/app_pages.dart';

class SettingsPage extends BasePage {
  const SettingsPage({Key? key}) : super(key: key);

  @override
  String get title => '设置';

  @override
  Widget buildBody(BuildContext context) {
    final controller = Get.find<SettingsController>();
    
    return ListView(
      children: [
        // 主题设置
        ListTile(
          title: const Text('主题设置'),
          trailing: Obx(() => DropdownButton<ThemeMode>(
            value: controller.themeMode.value,
            items: const [
              DropdownMenuItem(
                value: ThemeMode.system,
                child: Text('跟随系统'),
              ),
              DropdownMenuItem(
                value: ThemeMode.light,
                child: Text('浅色'),
              ),
              DropdownMenuItem(
                value: ThemeMode.dark,
                child: Text('深色'),
              ),
            ],
            onChanged: controller.setThemeMode,
          )),
        ),
        
        // 字体大小
        ListTile(
          title: const Text('字体大小'),
          trailing: Obx(() => Slider(
            value: controller.fontSize.value,
            min: 12,
            max: 24,
            divisions: 12,
            label: controller.fontSize.value.toString(),
            onChanged: controller.setFontSize,
          )),
        ),
        
        // 同步设置
        ListTile(
          title: const Text('同步设置'),
          trailing: const Icon(Icons.arrow_forward_ios),
          onTap: () => Get.toNamed('/settings/sync'),
        ),
        
        // 关于
        ListTile(
          title: const Text('关于'),
          trailing: const Icon(Icons.arrow_forward_ios),
          onTap: () => Get.toNamed('/settings/about'),
        ),
        
        // 登录安全
        ListTile(
          leading: const Icon(Icons.security),
          title: const Text('登录安全'),
          trailing: const Icon(Icons.chevron_right),
          onTap: () => Get.toNamed(Routes.LOGIN_SECURITY),
        ),
        
        // 登录通知
        ListTile(
          leading: const Icon(Icons.notifications),
          title: const Text('登录通知'),
          trailing: const Icon(Icons.chevron_right),
          onTap: () => Get.toNamed(Routes.LOGIN_NOTIFICATION),
        ),
      ],
    );
  }
} 