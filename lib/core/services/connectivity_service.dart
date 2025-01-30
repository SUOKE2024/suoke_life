import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:get/get.dart';

class ConnectivityService extends GetxService {
  final _connectivity = Connectivity();
  final isConnected = false.obs;
  final connectionType = Rx<ConnectivityResult>(ConnectivityResult.none);

  @override
  void onInit() {
    super.onInit();
    _initConnectivity();
    _setupConnectivityStream();
  }

  Future<void> _initConnectivity() async {
    try {
      final result = await _connectivity.checkConnectivity();
      _updateConnectionStatus(result);
    } catch (e) {
      debugPrint('初始化网络状态检查失败: $e');
    }
  }

  void _setupConnectivityStream() {
    _connectivity.onConnectivityChanged.listen((result) {
      _updateConnectionStatus(result);
      _notifyStatusChange(result);
    });
  }

  void _updateConnectionStatus(ConnectivityResult result) {
    connectionType.value = result;
    isConnected.value = result != ConnectivityResult.none;
  }

  void _notifyStatusChange(ConnectivityResult result) {
    if (result == ConnectivityResult.none) {
      Get.snackbar(
        '提示',
        '网络���接已断开',
        snackPosition: SnackPosition.TOP,
        duration: const Duration(seconds: 3),
      );
    } else {
      Get.snackbar(
        '提示',
        '网络已连接',
        snackPosition: SnackPosition.TOP,
        duration: const Duration(seconds: 3),
      );
    }
  }

  bool get hasConnection => isConnected.value;
  
  // 获取当前网络类型
  String get currentConnectionType {
    switch (connectionType.value) {
      case ConnectivityResult.mobile:
        return '移动网络';
      case ConnectivityResult.wifi:
        return 'WiFi';
      case ConnectivityResult.ethernet:
        return '以太网';
      case ConnectivityResult.vpn:
        return 'VPN';
      case ConnectivityResult.none:
        return '无网络';
      default:
        return '未知';
    }
  }
} 