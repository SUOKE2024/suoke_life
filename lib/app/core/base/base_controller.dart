import 'package:get/get.dart';

/// 基础控制器
abstract class BaseController extends GetxController {
  final _isLoading = false.obs;
  bool get isLoading => _isLoading.value;

  void showLoading() {
    _isLoading.value = true;
  }

  void hideLoading() {
    _isLoading.value = false;
  }

  void showError(String message) {
    hideLoading();
    Get.snackbar('错误', message);
  }

  void showSuccess(String message) {
    hideLoading();
    Get.snackbar('成功', message);
  }

  void handleError(dynamic error) {
    showError(error.toString());
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