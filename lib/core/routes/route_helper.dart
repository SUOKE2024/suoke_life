import 'package:get/get.dart';
import 'route_paths.dart';

class RouteHelper {
  // 基础导航方法
  static Future<T?>? to<T>(String route, {dynamic arguments}) {
    return Get.toNamed<T>(route, arguments: arguments);
  }
  
  static Future<T?>? off<T>(String route, {dynamic arguments}) {
    return Get.offNamed<T>(route, arguments: arguments);
  }
  
  static Future<T?>? offAll<T>(String route, {dynamic arguments}) {
    return Get.offAllNamed<T>(route, arguments: arguments);
  }
  
  static void back<T>({T? result}) {
    Get.back<T>(result: result);
  }
  
  // 常用页面导航方法
  static Future<void> toLogin() {
    return Get.offAllNamed(RoutePaths.login);
  }
  
  static Future<void> toMain() {
    return Get.offAllNamed(RoutePaths.main);
  }
  
  static Future<void> toRegister() {
    return Get.toNamed(RoutePaths.register);
  }
  
  static Future<void> toProfile() {
    return Get.toNamed(RoutePaths.profile);
  }
  
  static Future<void> toSettings() {
    return Get.toNamed(RoutePaths.settings);
  }
  
  static Future<void> toChat() {
    return Get.toNamed(RoutePaths.chat);
  }
  
  static Future<void> toChatList() {
    return Get.toNamed(RoutePaths.chatList);
  }
  
  static Future<void> toService() {
    return Get.toNamed(RoutePaths.service);
  }
  
  static Future<void> toProduct() {
    return Get.toNamed(RoutePaths.product);
  }
  
  static Future<void> toProductDetail(String productId) {
    return Get.toNamed(RoutePaths.productDetail, arguments: {'id': productId});
  }
  
  static Future<void> toCart() {
    return Get.toNamed(RoutePaths.cart);
  }
  
  static Future<void> toCheckout() {
    return Get.toNamed(RoutePaths.checkout);
  }
  
  static Future<void> toOrderList() {
    return Get.toNamed(RoutePaths.orderList);
  }
  
  static Future<void> toOrderDetail(String orderId) {
    return Get.toNamed(RoutePaths.orderDetail, arguments: {'id': orderId});
  }
  
  static Future<void> toCommunity() {
    return Get.toNamed(RoutePaths.community);
  }
  
  // 对话框方法
  static Future<T?> showLoading<T>({String? message}) {
    return Get.dialog(
      WillPopScope(
        onWillPop: () async => false,
        child: Center(
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Get.theme.cardColor,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const CircularProgressIndicator(),
                if (message != null) ...[
                  const SizedBox(height: 16),
                  Text(message),
                ],
              ],
            ),
          ),
        ),
      ),
      barrierDismissible: false,
    );
  }
  
  static void hideLoading() {
    if (Get.isDialogOpen ?? false) {
      Get.back();
    }
  }
  
  static Future<bool?> showConfirmDialog({
    String? title,
    String? message,
    String? confirmText,
    String? cancelText,
  }) {
    return Get.dialog<bool>(
      AlertDialog(
        title: title == null ? null : Text(title),
        content: message == null ? null : Text(message),
        actions: [
          TextButton(
            onPressed: () => Get.back(result: false),
            child: Text(cancelText ?? '取消'),
          ),
          TextButton(
            onPressed: () => Get.back(result: true),
            child: Text(confirmText ?? '确定'),
          ),
        ],
      ),
    );
  }
  
  static void showSnackbar({
    String? title,
    String? message,
    Duration duration = const Duration(seconds: 2),
  }) {
    Get.snackbar(
      title ?? '',
      message ?? '',
      duration: duration,
      snackPosition: SnackPosition.BOTTOM,
    );
  }
  
  static void showError(String message) {
    Get.snackbar(
      '错误',
      message,
      backgroundColor: Get.theme.colorScheme.error,
      colorText: Get.theme.colorScheme.onError,
      duration: const Duration(seconds: 3),
      snackPosition: SnackPosition.BOTTOM,
    );
  }
  
  static void showSuccess(String message) {
    Get.snackbar(
      '成功',
      message,
      backgroundColor: Get.theme.colorScheme.primary,
      colorText: Get.theme.colorScheme.onPrimary,
      duration: const Duration(seconds: 2),
      snackPosition: SnackPosition.BOTTOM,
    );
  }
} 