import 'package:get/get.dart';
import '../../data/models/device_info.dart';
import '../../services/device_service.dart';

class DeviceController extends GetxController {
  final DeviceService _deviceService;
  final devices = <DeviceInfo>[].obs;
  final isLoading = false.obs;
  final error = Rx<String?>(null);

  DeviceController({
    required DeviceService deviceService,
  }) : _deviceService = deviceService;

  @override
  void onInit() {
    super.onInit();
    loadDevices();
  }

  Future<void> loadDevices() async {
    try {
      isLoading.value = true;
      error.value = null;
      final result = await _deviceService.getDevices();
      devices.assignAll(result);
    } catch (e) {
      error.value = '加载设备列表失败';
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> addDevice(DeviceInfo device) async {
    try {
      await _deviceService.addDevice(device);
      devices.add(device);
      Get.back();
      Get.snackbar('成功', '添加设备成功');
    } catch (e) {
      Get.snackbar('错误', '添加设备失败');
    }
  }

  Future<void> removeDevice(String deviceId) async {
    try {
      await _deviceService.removeDevice(deviceId);
      devices.removeWhere((d) => d.id == deviceId);
      Get.snackbar('成功', '移除设备成功');
    } catch (e) {
      Get.snackbar('错误', '移除设备失败');
    }
  }

  Future<void> updateDevice(DeviceInfo device) async {
    try {
      await _deviceService.updateDevice(device);
      final index = devices.indexWhere((d) => d.id == device.id);
      if (index != -1) {
        devices[index] = device;
      }
      Get.back();
      Get.snackbar('成功', '更新设备成功');
    } catch (e) {
      Get.snackbar('错误', '更新设备失败');
    }
  }

  Future<void> syncDevice(String deviceId) async {
    try {
      await _deviceService.syncDevice(deviceId);
      Get.snackbar('成功', '同步设备成功');
    } catch (e) {
      Get.snackbar('错误', '同步设备失败');
    }
  }
} 