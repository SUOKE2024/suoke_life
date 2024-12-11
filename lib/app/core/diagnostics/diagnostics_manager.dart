class DiagnosticsManager {
  static final instance = DiagnosticsManager._();
  DiagnosticsManager._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  
  final _diagnosticResults = <DiagnosticResult>[].obs;
  final _isRunning = false.obs;

  Future<void> runDiagnostics() async {
    if (_isRunning.value) return;

    _isRunning.value = true;
    _diagnosticResults.clear();
    _eventBus.fire(DiagnosticsStartedEvent());

    try {
      // 系统信息检查
      await _checkSystemInfo();
      
      // 存储空间检查
      await _checkStorage();
      
      // 网络连接检查
      await _checkNetwork();
      
      // 数据库检查
      await _checkDatabase();
      
      // 文件完整性检查
      await _checkFiles();
      
      // 性能检查
      await _checkPerformance();
      
      _eventBus.fire(DiagnosticsCompletedEvent(_diagnosticResults));
    } catch (e) {
      _eventBus.fire(DiagnosticsFailedEvent(e));
    } finally {
      _isRunning.value = false;
    }
  }

  Future<void> _checkSystemInfo() async {
    final deviceInfo = Get.find<DeviceManager>();
    
    _addResult(DiagnosticResult(
      type: DiagnosticType.systemInfo,
      name: 'System Information',
      details: {
        'os': Platform.operatingSystem,
        'version': Platform.operatingSystemVersion,
        'model': deviceInfo.deviceModel,
        'manufacturer': deviceInfo.deviceInfo.manufacturer,
        'isPhysicalDevice': deviceInfo.isPhysicalDevice,
      },
    ));
  }

  Future<void> _checkStorage() async {
    final appDir = await getApplicationDocumentsDirectory();
    final totalSpace = await DiskSpace.getTotalDiskSpace();
    final freeSpace = await DiskSpace.getFreeDiskSpace();
    
    _addResult(DiagnosticResult(
      type: DiagnosticType.storage,
      name: 'Storage',
      details: {
        'totalSpace': totalSpace,
        'freeSpace': freeSpace,
        'usedSpace': totalSpace - freeSpace,
        'appStoragePath': appDir.path,
      },
      status: freeSpace / totalSpace < 0.1 
          ? DiagnosticStatus.warning 
          : DiagnosticStatus.ok,
    ));
  }

  Future<void> _checkNetwork() async {
    final networkInfo = Get.find<NetworkMonitor>();
    final connectionTest = await _testConnection();
    
    _addResult(DiagnosticResult(
      type: DiagnosticType.network,
      name: 'Network',
      details: {
        'isOnline': networkInfo.isOnline,
        'connectionType': networkInfo.connectionStatus.toString(),
        'pingLatency': connectionTest.latency,
        'downloadSpeed': connectionTest.downloadSpeed,
        'uploadSpeed': connectionTest.uploadSpeed,
      },
      status: !networkInfo.isOnline 
          ? DiagnosticStatus.error
          : connectionTest.latency > 500 
              ? DiagnosticStatus.warning 
              : DiagnosticStatus.ok,
    ));
  }

  Future<void> _checkDatabase() async {
    try {
      final dbService = Get.find<DatabaseService>();
      final integrity = await dbService.checkIntegrity();
      
      _addResult(DiagnosticResult(
        type: DiagnosticType.database,
        name: 'Database',
        details: {
          'size': await dbService.getDatabaseSize(),
          'tables': await dbService.getTableCount(),
          'lastBackup': await dbService.getLastBackupTime(),
        },
        status: integrity ? DiagnosticStatus.ok : DiagnosticStatus.error,
      ));
    } catch (e) {
      _addResult(DiagnosticResult(
        type: DiagnosticType.database,
        name: 'Database',
        details: {'error': e.toString()},
        status: DiagnosticStatus.error,
      ));
    }
  }

  Future<void> _checkFiles() async {
    final resourceManager = Get.find<ResourceManager>();
    final missingFiles = await resourceManager.checkMissingFiles();
    
    _addResult(DiagnosticResult(
      type: DiagnosticType.files,
      name: 'Files',
      details: {
        'totalFiles': await resourceManager.getTotalFiles(),
        'missingFiles': missingFiles.length,
        'corruptedFiles': await resourceManager.getCorruptedFiles(),
      },
      status: missingFiles.isEmpty 
          ? DiagnosticStatus.ok 
          : DiagnosticStatus.warning,
    ));
  }

  Future<void> _checkPerformance() async {
    final performanceMonitor = Get.find<PerformanceMonitor>();
    final metrics = performanceMonitor.getMetrics();
    
    _addResult(DiagnosticResult(
      type: DiagnosticType.performance,
      name: 'Performance',
      details: {
        'averageFrameTime': metrics.averageFrameTime,
        'memoryUsage': metrics.memoryUsage,
        'cpuUsage': metrics.cpuUsage,
        'batteryLevel': metrics.batteryLevel,
      },
      status: metrics.hasPerformanceIssues
          ? DiagnosticStatus.warning
          : DiagnosticStatus.ok,
    ));
  }

  void _addResult(DiagnosticResult result) {
    _diagnosticResults.add(result);
    _eventBus.fire(DiagnosticResultAddedEvent(result));
  }

  Future<String> generateReport() async {
    final buffer = StringBuffer();
    buffer.writeln('Diagnostic Report');
    buffer.writeln('Generated: ${DateTime.now()}');
    buffer.writeln();

    for (final result in _diagnosticResults) {
      buffer.writeln('${result.name} (${result.status})');
      result.details.forEach((key, value) {
        buffer.writeln('  $key: $value');
      });
      buffer.writeln();
    }

    return buffer.toString();
  }

  List<DiagnosticResult> get results => List.unmodifiable(_diagnosticResults);
  bool get isRunning => _isRunning.value;
}

class DiagnosticResult {
  final DiagnosticType type;
  final String name;
  final Map<String, dynamic> details;
  final DiagnosticStatus status;

  DiagnosticResult({
    required this.type,
    required this.name,
    required this.details,
    this.status = DiagnosticStatus.ok,
  });
}

enum DiagnosticType {
  systemInfo,
  storage,
  network,
  database,
  files,
  performance,
}

enum DiagnosticStatus {
  ok,
  warning,
  error,
}

// 诊断相关事件
class DiagnosticsStartedEvent extends AppEvent {}

class DiagnosticsCompletedEvent extends AppEvent {
  final List<DiagnosticResult> results;
  DiagnosticsCompletedEvent(this.results);
}

class DiagnosticsFailedEvent extends AppEvent {
  final dynamic error;
  DiagnosticsFailedEvent(this.error);
}

class DiagnosticResultAddedEvent extends AppEvent {
  final DiagnosticResult result;
  DiagnosticResultAddedEvent(this.result);
} 