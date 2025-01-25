import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/device_manager_controller.dart';
import '../../widgets/device_list_item.dart';

class DeviceManagerPage extends BasePage<DeviceManagerController> {
  const DeviceManagerPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('设备管理'),
      actions: [
        IconButton(
          icon: const Icon(Icons.delete_sweep),
          onPressed: controller.showRevokeAllDialog,
        ),
      ],
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return Obx(() {
      if (controller.isLoading.value) {
        return const Center(child: CircularProgressIndicator());
      }

      if (controller.devices.isEmpty) {
        return Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.devices,
                size: 64,
                color: Colors.grey[400],
              ),
              const SizedBox(height: 16),
              Text(
                '暂无登录设备',
                style: Get.textTheme.titleMedium?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        );
      }

      return RefreshIndicator(
        onRefresh: controller.refreshDevices,
        child: ListView.separated(
          padding: const EdgeInsets.all(16),
          itemCount: controller.devices.length,
          separatorBuilder: (_, __) => const Divider(height: 1),
          itemBuilder: (context, index) {
            final device = controller.devices[index];
            return DeviceListItem(
              device: device,
              isCurrentDevice: controller.isCurrentDevice(device.id),
              onRename: () => controller.showRenameDialog(device),
              onRevoke: () => controller.showRevokeDialog(device),
            );
          },
        ),
      );
    });
  }
} 