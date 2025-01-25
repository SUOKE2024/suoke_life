import 'package:flutter/foundation.dart';

abstract class BaseController {
  final isLoading = ValueNotifier<bool>(false);
  final error = ValueNotifier<String?>(null);

  void setLoading(bool value) {
    isLoading.value = value;
  }

  void setError(String? message) {
    error.value = message;
  }

  void dispose() {
    isLoading.dispose();
    error.dispose();
  }
} 