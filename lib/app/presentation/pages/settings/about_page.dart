import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/settings/about_controller.dart';

class AboutPage extends GetView<AboutController> {
  const AboutPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('关于'),
      ),
      body: ListView(
        children: [
          // Logo和版本信息
          Container(
            padding: const EdgeInsets.all(32),
            child: Column(
              children: [
                Image.asset(
                  'assets/images/logo.png',
                  width: 100,
                  height: 100,
                ),
                const SizedBox(height: 16),
                const Text(
                  '索克生活',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Obx(() => Text(
                  'Version ${controller.version.value}',
                  style: TextStyle(
                    color: Colors.grey[600],
                  ),
                )),
              ],
            ),
          ),

          const Divider(),

          // 功能列表
          ListTile(
            title: const Text('检查更新'),
            trailing: const Icon(Icons.chevron_right),
            onTap: controller.checkUpdate,
          ),
          ListTile(
            title: const Text('用户协议'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => Get.toNamed('/settings/terms'),
          ),
          ListTile(
            title: const Text('隐私政策'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => Get.toNamed('/settings/privacy'),
          ),
          ListTile(
            title: const Text('开源许可'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => Get.toNamed('/settings/licenses'),
          ),
        ],
      ),
    );
  }
} 