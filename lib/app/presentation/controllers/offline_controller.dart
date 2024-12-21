import 'package:get/get.dart';
import '../../services/connectivity_service.dart';

class OfflineController extends GetxController {
  final _connectivityService = Get.find<ConnectivityService>();
  final isChecking = false.obs;

  Future<void> checkConnection() async {
    isChecking.value = true;
    
    try {
      await Future.delayed(const Duration(seconds: 1));
      if (_connectivityService.hasConnection) {
        Get.back();
      } else {
        Get.snackbar(
          '提示',
          '网络连接仍未恢复',
          snackPosition: SnackPosition.BOTTOM,
        );
      }
    } finally {
      isChecking.value = false;
    }
  }
} 