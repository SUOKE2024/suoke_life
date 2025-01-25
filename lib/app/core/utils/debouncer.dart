import 'dart:async';
import 'package:flutter/foundation.dart';

class Debouncer {
  final Duration duration;
  Timer? _timer;
  bool _disposed = false;

  Debouncer({required int milliseconds})
      : assert(milliseconds > 0, 'milliseconds must be positive'),
        duration = Duration(milliseconds: milliseconds);

  void run(VoidCallback action) {
    assert(!_disposed, 'Debouncer has been disposed');
    if (_disposed) return;
    _timer?.cancel();
    _timer = Timer(duration, action);
  }

  void cancel() {
    assert(!_disposed, 'Debouncer has been disposed');
    _timer?.cancel();
    _timer = null;
  }

  void dispose() {
    assert(!_disposed, 'Debouncer already disposed');
    cancel();
    _disposed = true;
  }
} 