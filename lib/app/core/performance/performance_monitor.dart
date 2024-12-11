class PerformanceMonitor {
  static final instance = PerformanceMonitor._();
  PerformanceMonitor._();

  final _metrics = <String, PerformanceMetric>{};
  final _traces = <String, Trace>{};
  
  bool _isEnabled = false;
  final _logger = Get.find<LoggerManager>();

  void startTrace(String name) {
    if (!_isEnabled) return;
    
    final trace = Trace(name: name);
    _traces[name] = trace;
  }

  void endTrace(String name) {
    if (!_isEnabled) return;
    
    final trace = _traces.remove(name);
    if (trace != null) {
      final duration = trace.end();
      _recordMetric(name, duration);
    }
  }

  void _recordMetric(String name, Duration duration) {
    final metric = _metrics.putIfAbsent(
      name,
      () => PerformanceMetric(name: name),
    );
    
    metric.addSample(duration);
    
    if (metric.samples.length >= 100) {
      _reportMetrics(name);
    }
  }

  void _reportMetrics(String name) {
    final metric = _metrics[name];
    if (metric == null) return;

    _logger.info('Performance metric: $name', {
      'average': metric.average.inMilliseconds,
      'min': metric.min.inMilliseconds,
      'max': metric.max.inMilliseconds,
      'samples': metric.samples.length,
    });

    metric.reset();
  }

  void enable() => _isEnabled = true;
  void disable() => _isEnabled = false;
}

class Trace {
  final String name;
  final DateTime startTime;
  DateTime? endTime;

  Trace({required this.name}) : startTime = DateTime.now();

  Duration end() {
    endTime = DateTime.now();
    return endTime!.difference(startTime);
  }
}

class PerformanceMetric {
  final String name;
  final List<Duration> samples = [];

  PerformanceMetric({required this.name});

  void addSample(Duration duration) {
    samples.add(duration);
  }

  Duration get average {
    if (samples.isEmpty) return Duration.zero;
    final total = samples.fold<int>(
      0,
      (sum, duration) => sum + duration.inMicroseconds,
    );
    return Duration(microseconds: total ~/ samples.length);
  }

  Duration get min => samples.reduce((a, b) => a < b ? a : b);
  Duration get max => samples.reduce((a, b) => a > b ? a : b);

  void reset() => samples.clear();
} 