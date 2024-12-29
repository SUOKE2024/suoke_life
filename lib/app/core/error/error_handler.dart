import 'package:get/get.dart';

class ErrorHandler {
  static void handleError(dynamic error, StackTrace? stackTrace) {
    // 记录错误
    print('Error: $error');
    if (stackTrace != null) {
      print('StackTrace: $stackTrace');
    }

    // 分类处理
    if (error is NetworkError) {
      Get.snackbar(
        '网络错误',
        '请检查网络连接后重试',
        duration: const Duration(seconds: 3),
      );
    } else if (error is AuthenticationError) {
      Get.offAllNamed('/login');
    } else if (error is AccessibilityError) {
      // 无障碍相关错误处理
      Get.dialog(
        AccessibilityErrorDialog(error: error),
      );
    } else {
      Get.snackbar(
        '错误',
        error.toString(),
        duration: const Duration(seconds: 3),
      );
    }
  }
} 