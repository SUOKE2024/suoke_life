abstract class BaseState<T> extends GetxController {
  final _isLoading = false.obs;
  final _error = Rxn<String>();
  final _data = Rxn<T>();

  bool get isLoading => _isLoading.value;
  String? get error => _error.value;
  T? get data => _data.value;

  @protected
  Future<void> runAsync(Future<void> Function() action) async {
    try {
      _isLoading.value = true;
      _error.value = null;
      await action();
    } catch (e) {
      _error.value = e.toString();
      AppErrorHandler.handleError(e);
    } finally {
      _isLoading.value = false;
    }
  }

  @protected
  void updateData(T newData) {
    _data.value = newData;
  }
} 