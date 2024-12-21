import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/network_settings_controller.dart';
import '../../widgets/network_status_indicator.dart';

class NetworkSettingsPage extends BasePage<NetworkSettingsController> {
  const NetworkSettingsPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('网络设置'),
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // 网络状态卡片
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '当前网络状态',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                const Center(child: NetworkStatusIndicator()),
                const SizedBox(height: 16),
                Obx(() => Text(
                  '上次检查: ${controller.lastCheckTime}',
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 12,
                  ),
                )),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // 网络设置选项
        Card(
          child: Column(
            children: [
              ListTile(
                title: const Text('自动检查网络'),
                subtitle: const Text('定期检查网络连接状态'),
                trailing: Obx(() => Switch(
                  value: controller.autoCheck.value,
                  onChanged: controller.setAutoCheck,
                )),
              ),
              const Divider(height: 1),
              ListTile(
                title: const Text('网络异常提醒'),
                subtitle: const Text('网络状态变化时显示提示'),
                trailing: Obx(() => Switch(
                  value: controller.showNotification.value,
                  onChanged: controller.setShowNotification,
                )),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // 网络诊断
        Card(
          child: Column(
            children: [
              ListTile(
                leading: const Icon(Icons.network_check),
                title: const Text('网络诊断'),
                subtitle: const Text('检查网络连接问题'),
                trailing: const Icon(Icons.chevron_right),
                onTap: controller.runDiagnostics,
              ),
              const Divider(height: 1),
              ListTile(
                leading: const Icon(Icons.history),
                title: const Text('连接历史'),
                subtitle: const Text('查看网络连接记录'),
                trailing: const Icon(Icons.chevron_right),
                onTap: controller.showConnectionHistory,
              ),
            ],
          ),
        ),
      ],
    );
  }
} 