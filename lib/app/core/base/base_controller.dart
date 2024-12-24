import 'package:get/get.dart';

/// 基础控制器
abstract class BaseController extends GetxController {
  final RxBool isLoading = false.obs;
  final RxString error = ''.obs;
  
  void setLoading(bool value) => isLoading.value = value;
  void setError(String message) => error.value = message;
  void clearError() => error.value = '';
  
  @override
  void onInit() {
    super.onInit();
  }
  
  @override
  void onClose() {
    super.onClose();
  }
} 