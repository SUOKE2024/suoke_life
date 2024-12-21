import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/offline_controller.dart';

class OfflinePage extends BasePage<OfflineController> {
  const OfflinePage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('网络连接已断开'),
      leading: IconButton(
        icon: const Icon(Icons.arrow_back),
        onPressed: () => Get.back(),
      ),
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.cloud_off,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            '网络连接已断开',
            style: Get.textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          Text(
            '请检查网络设置后重试',
            style: Get.textTheme.bodyMedium?.copyWith(
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 32),
          Obx(() => controller.isChecking.value
            ? const CircularProgressIndicator()
            : ElevatedButton.icon(
                onPressed: controller.checkConnection,
                icon: const Icon(Icons.refresh),
                label: const Text('重试'),
              ),
          ),
        ],
      ),
    );
  }
} 