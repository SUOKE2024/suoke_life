import 'package:get/get.dart';

/// 基础控制器
abstract class BaseController extends GetxController {
  final isLoading = false.obs;
  final errorMessage = ''.obs;
  
  void showLoading() => isLoading.value = true;
  void hideLoading() => isLoading.value = false;
  
  void showError(String message) {
    errorMessage.value = message;
    Get.snackbar(
      '错误',
      message,
      snackPosition: SnackPosition.BOTTOM,
    );
  }
  
  void showSuccess(String message) {
    Get.snackbar(
      '成功',
      message,
      snackPosition: SnackPosition.BOTTOM,
    );
  }
  
  @override
  void onInit() {
    super.onInit();
  }
  
  @override
  void onClose() {
    super.onClose();
  }
} 