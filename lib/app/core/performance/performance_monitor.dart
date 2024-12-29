import 'package:get/get.dart';

class PerformanceMonitor {
  static final _instance = PerformanceMonitor._();
  factory PerformanceMonitor() => _instance;
  PerformanceMonitor._();

  final _metrics = <String, List<int>>{}.obs;
  
  void startOperation(String name) {
    if (!_metrics.containsKey(name)) {
      _metrics[name] = [];
    }
    _metrics[name]!.add(DateTime.now().millisecondsSinceEpoch);
  }

  void endOperation(String name) {
    if (_metrics.containsKey(name)) {
      final start = _metrics[name]!.last;
      final duration = DateTime.now().millisecondsSinceEpoch - start;
      print('Operation $name took $duration ms');
      
      if (duration > 1000) { // 超过1秒的操作
        Get.snackbar(
          '性能警告',
          '操作 $name 耗时过长: ${duration}ms',
          duration: const Duration(seconds: 3),
        );
      }
    }
  }
} 