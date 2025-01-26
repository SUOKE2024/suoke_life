import 'package:injectable/injectable.dart';
import 'package:flutter/foundation.dart';
import '../base/base_controller.dart';

@injectable
class ControllerTemplate extends BaseController {
  final ValueNotifier<bool> loading = ValueNotifier<bool>(false);
  @override
  final ValueNotifier<String?> error = ValueNotifier<String?>(null);

  @override
  void setLoading(bool value) {
    loading.value = value;
  }

  @override
  void setError(String? message) {
    error.value = message;
  }

  @override
  void dispose() {
    loading.dispose();
    error.dispose();
    super.dispose();
  }
}
