import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../routes/app_routes.dart';
import '../../../controllers/settings_controller.dart';

class SettingsPage extends GetView<SettingsController> {
  const SettingsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: ListView(
        children: [
          ListTile(
            title: const Text('Theme Mode'),
            trailing: Obx(() => DropdownButton<ThemeMode>(
              value: controller.themeMode.value,
              onChanged: (ThemeMode? mode) {
                if (mode != null) {
                  controller.setThemeMode(mode);
                }
              },
              items: ThemeMode.values.map((ThemeMode mode) {
                return DropdownMenuItem(
                  value: mode,
                  child: Text(mode.toString()),
                );
              }).toList(),
            )),
          ),
          ListTile(
            title: const Text('Font Size'),
            trailing: Obx(() => Slider(
              value: controller.fontSize.value,
              min: 12,
              max: 24,
              divisions: 12,
              label: controller.fontSize.value.toString(),
              onChanged: controller.setFontSize,
            )),
          ),
          ListTile(
            title: const Text('Security'),
            trailing: const Icon(Icons.arrow_forward_ios),
            onTap: () => Get.toNamed(Routes.LOGIN_SECURITY),
          ),
          ListTile(
            title: const Text('Notifications'),
            trailing: const Icon(Icons.arrow_forward_ios),
            onTap: () => Get.toNamed(Routes.LOGIN_NOTIFICATION),
          ),
        ],
      ),
    );
  }
} 