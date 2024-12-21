import 'package:get/get.dart';
import '../../services/connectivity_service.dart';
import '../../core/services/storage_service.dart';
import '../../core/constants/storage_keys.dart';

class NetworkSettingsController extends GetxController {
  final _connectivityService = Get.find<ConnectivityService>();
  final _storage = Get.find<StorageService>();

  final autoCheck = true.obs;
  final showNotification = true.obs;
  final lastCheckTime = ''.obs;

  @override
  void onInit() {
    super.onInit();
    _loadSettings();
    _updateLastCheckTime();
  }

  Future<void> _loadSettings() async {
    autoCheck.value = _storage.getBool(StorageKeys.networkAutoCheck) ?? true;
    showNotification.value = _storage.getBool(StorageKeys.networkNotification) ?? true;
  }

  Future<void> setAutoCheck(bool value) async {
    autoCheck.value = value;
    await _storage.setBool(StorageKeys.networkAutoCheck, value);
  }

  Future<void> setShowNotification(bool value) async {
    showNotification.value = value;
    await _storage.setBool(StorageKeys.networkNotification, value);
  }

  void _updateLastCheckTime() {
    lastCheckTime.value = DateTime.now().toString().substring(0, 19);
  }

  Future<void> runDiagnostics() async {
    Get.dialog(
      const Center(child: CircularProgressIndicator()),
      barrierDismissible: false,
    );

    await Future.delayed(const Duration(seconds: 2));
    Get.back();

    final isConnected = _connectivityService.hasConnection;
    final connectionType = _connectivityService.currentConnectionType;

    Get.dialog(
      AlertDialog(
        title: const Text('诊断结果'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('网络状态: ${isConnected ? "已连接" : "未连接"}'),
            const SizedBox(height: 8),
            Text('连接类型: $connectionType'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('确定'),
          ),
        ],
      ),
    );

    _updateLastCheckTime();
  }

  void showConnectionHistory() {
    // TODO: 实现连接历史页面
    Get.toNamed('/settings/network/history');
  }
} 