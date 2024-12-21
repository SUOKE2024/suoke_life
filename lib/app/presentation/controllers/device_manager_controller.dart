import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../services/device_manager_service.dart';
import '../../data/models/device_info.dart';
import '../../core/base/base_controller.dart';

class DeviceManagerController extends BaseController {
  final _deviceManager = Get.find<DeviceManagerService>();
  
  final devices = <DeviceInfo>[].obs;
  final nameController = TextEditingController();

  @override
  void onInit() {
    super.onInit();
    loadDevices();
  }

  @override
  void onClose() {
    nameController.dispose();
    super.onClose();
  }

  Future<void> loadDevices() async {
    try {
      showLoading();
      devices.value = await _deviceManager.getDevices();
      hideLoading();
    } catch (e) {
      hideLoading();
      showError(e.toString());
    }
  }

  Future<void> refreshDevices() => loadDevices();

  bool isCurrentDevice(String deviceId) {
    return _deviceManager.isCurrentDevice(deviceId);
  }

  void showRenameDialog(DeviceInfo device) {
    nameController.text = device.deviceName;
    Get.dialog(
      AlertDialog(
        title: const Text('重命名设备'),
        content: TextField(
          controller: nameController,
          decoration: const InputDecoration(
            labelText: '设备名称',
            hintText: '请输入新的设备名称',
          ),
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () async {
              if (nameController.text.isEmpty) {
                showError('设备名称不能为空');
                return;
              }
              Get.back();
              try {
                await _deviceManager.updateDeviceName(
                  device.id,
                  nameController.text,
                );
              } catch (e) {
                showError(e.toString());
              }
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  void showRevokeDialog(DeviceInfo device) {
    Get.dialog(
      AlertDialog(
        title: const Text('移除设备'),
        content: Text('确定要移除设备"${device.deviceName}"吗？'),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () async {
              Get.back();
              try {
                await _deviceManager.revokeDevice(device.id);
              } catch (e) {
                showError(e.toString());
              }
            },
            child: const Text(
              '移除',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }

  void showRevokeAllDialog() {
    Get.dialog(
      AlertDialog(
        title: const Text('移除其他设备'),
        content: const Text('确定要移除除当前设备外的所有设备吗？'),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () async {
              Get.back();
              try {
                await _deviceManager.revokeAllOtherDevices();
              } catch (e) {
                showError(e.toString());
              }
            },
            child: const Text(
              '移除',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }
} 