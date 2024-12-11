/// 基础控制器
abstract class BaseController extends GetxController {
  final _loading = false.obs;
  final _error = Rxn<String>();
  
  bool get loading => _loading.value;
  String? get error => _error.value;

  /// 执行异步操作
  Future<T> runAsync<T>(
    Future<T> Function() action, {
    String? loadingMessage,
    bool showError = true,
  }) async {
    try {
      _loading.value = true;
      _error.value = null;
      return await action();
    } catch (e) {
      _error.value = e.toString();
      if (showError) {
        Get.snackbar('Error', e.toString());
      }
      rethrow;
    } finally {
      _loading.value = false;
    }
  }
} 