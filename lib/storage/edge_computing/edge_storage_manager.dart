import 'dart:async';
import '../local/base_storage.dart';
import '../remote/mcp_storage_adapter.dart';
import '../remote/oss_storage_adapter.dart';
import '../remote/db_storage_adapter.dart';
import 'value_analyzer.dart';
import 'resource_monitor.dart';
import 'local_ai_processor.dart';

/// 边缘存储管理器
class EdgeStorageManager {
  final BaseStorage _localStorage;
  final MCPStorageAdapter _mcpStorage;
  final OSSStorageAdapter _ossStorage;
  final DBStorageAdapter _dbStorage;
  final ValueAnalyzer _valueAnalyzer;
  final ResourceMonitor _resourceMonitor;
  final LocalAIProcessor _aiProcessor;
  
  /// 同步配置
  final EdgeSyncConfig _syncConfig;
  
  /// 同步状态
  final _syncStatusController = StreamController<SyncStatus>.broadcast();
  Stream<SyncStatus> get syncStatusStream => _syncStatusController.stream;
  
  /// 存储策略
  final StoragePolicy _policy;
  
  EdgeStorageManager({
    required BaseStorage localStorage,
    required MCPStorageAdapter mcpStorage,
    required OSSStorageAdapter ossStorage,
    required DBStorageAdapter dbStorage,
    required ValueAnalyzer valueAnalyzer,
    required ResourceMonitor resourceMonitor,
    required LocalAIProcessor aiProcessor,
    EdgeSyncConfig? syncConfig,
    StoragePolicy? policy,
  }) : _localStorage = localStorage,
       _mcpStorage = mcpStorage,
       _ossStorage = ossStorage,
       _dbStorage = dbStorage,
       _valueAnalyzer = valueAnalyzer,
       _resourceMonitor = resourceMonitor,
       _aiProcessor = aiProcessor,
       _syncConfig = syncConfig ?? EdgeSyncConfig(),
       _policy = policy ?? StoragePolicy() {
    // 初始化同步任务
    _initializeSync();
  }
  
  /// 写入数据
  Future<void> write(String key, dynamic value) async {
    try {
      // 1. 分析数据价值
      final context = await _buildDataContext(key);
      final valueAnalysis = await _valueAnalyzer.analyzeValue(value, context);
      
      // 2. 确定存储策略
      final strategy = _policy.determineStrategy(valueAnalysis);
      
      // 3. 本地存储
      if (strategy.useLocalStorage) {
        await _localStorage.write(key, value);
      }
      
      // 4. 远程存储
      if (strategy.useRemoteStorage) {
        await _storeRemotely(key, value, strategy);
      }
      
      // 5. 处理高价值数据
      if (valueAnalysis.isValuable) {
        await _processValuableData(key, value, valueAnalysis);
      }
    } catch (e) {
      // 降级到本地存储
      await _localStorage.write(key, value);
      rethrow;
    }
  }
  
  /// 读取数据
  Future<T?> read<T>(String key) async {
    try {
      // 1. 检查本地缓存
      final localValue = await _localStorage.read<T>(key);
      if (localValue != null) {
        return localValue;
      }
      
      // 2. 尝试从远程读取
      final remoteValue = await _readFromRemote<T>(key);
      if (remoteValue != null) {
        // 缓存到本地
        await _localStorage.write(key, remoteValue);
      }
      
      return remoteValue;
    } catch (e) {
      // 降级到本地读取
      return _localStorage.read<T>(key);
    }
  }
  
  /// 删除数据
  Future<void> delete(String key) async {
    try {
      // 1. 删除本地数据
      await _localStorage.delete(key);
      
      // 2. 删除远程数据
      await Future.wait([
        _mcpStorage.delete(key),
        _ossStorage.deleteFile(key),
        _dbStorage.delete(key),
      ]);
    } catch (e) {
      // 确保本地数据被删除
      await _localStorage.delete(key);
      rethrow;
    }
  }
  
  /// 清理数据
  Future<void> clear() async {
    try {
      // 1. 清理本地数据
      await _localStorage.clear();
      
      // 2. 清理远程数据
      await Future.wait([
        _mcpStorage.clear(),
        // OSS和DB的清理需要谨慎，通常不建议完全清理
      ]);
    } catch (e) {
      // 确保本地数据被清理
      await _localStorage.clear();
      rethrow;
    }
  }
  
  /// 初始化同步任务
  void _initializeSync() {
    // 定期同步
    Timer.periodic(_syncConfig.syncInterval, (_) => _sync());
    
    // 监听资源状态变化
    _resourceMonitor.resourceStatusStream.listen((status) {
      if (_resourceMonitor.isReadyForSync(status)) {
        _sync();
      }
    });
  }
  
  /// 同步数据
  Future<void> _sync() async {
    if (!_syncStatusController.isClosed) {
      _syncStatusController.add(SyncStatus(state: SyncState.syncing));
    }
    
    try {
      // 1. 获取需要同步的数据
      final pendingSync = await _getPendingSyncData();
      
      // 2. 按优先级排序
      final sortedData = await _sortByPriority(pendingSync);
      
      // 3. 执行同步
      for (final item in sortedData) {
        await _syncItem(item);
      }
      
      if (!_syncStatusController.isClosed) {
        _syncStatusController.add(SyncStatus(
          state: SyncState.completed,
          lastSyncTime: DateTime.now(),
        ));
      }
    } catch (e) {
      if (!_syncStatusController.isClosed) {
        _syncStatusController.add(SyncStatus(
          state: SyncState.error,
          error: e.toString(),
        ));
      }
    }
  }
  
  /// 获取待同步数据
  Future<List<PendingSyncItem>> _getPendingSyncData() async {
    // TODO: 实现获取待同步数据的逻辑
    return [];
  }
  
  /// 按优先级排序
  Future<List<PendingSyncItem>> _sortByPriority(
    List<PendingSyncItem> items
  ) async {
    // 根据数据价值和紧急程度排序
    return items..sort((a, b) => b.priority.compareTo(a.priority));
  }
  
  /// 同步单个项目
  Future<void> _syncItem(PendingSyncItem item) async {
    try {
      switch (item.target) {
        case SyncTarget.mcp:
          await _mcpStorage.syncData(item.key, item.value);
          break;
        case SyncTarget.oss:
          if (item.value is String) {
            await _ossStorage.uploadFile(item.value, item.key);
          }
          break;
        case SyncTarget.db:
          await _dbStorage.write(item.key, item.value);
          break;
      }
    } catch (e) {
      print('Failed to sync item ${item.key}: $e');
      // 记录失败，稍后重试
    }
  }
  
  /// 远程存储
  Future<void> _storeRemotely(
    String key,
    dynamic value,
    StorageStrategy strategy,
  ) async {
    final futures = <Future>[];
    
    if (strategy.useMCP) {
      futures.add(_mcpStorage.write(key, value));
    }
    
    if (strategy.useOSS) {
      futures.add(_ossStorage.uploadFile(value, key));
    }
    
    if (strategy.useDB) {
      futures.add(_dbStorage.write(key, value));
    }
    
    await Future.wait(futures);
  }
  
  /// 从远程读取
  Future<T?> _readFromRemote<T>(String key) async {
    // 按优先级尝试不同的远程存储
    try {
      // 1. 优先从MCP读取
      final mcpValue = await _mcpStorage.read<T>(key);
      if (mcpValue != null) return mcpValue;
      
      // 2. 尝试从数据库读取
      final dbValue = await _dbStorage.read<T>(key);
      if (dbValue != null) return dbValue;
      
      // 3. 最后尝试从OSS读取
      final ossValue = await _ossStorage.downloadFile(key);
      return ossValue as T?;
    } catch (e) {
      return null;
    }
  }
  
  /// 处理高价值数据
  Future<void> _processValuableData(
    String key,
    dynamic value,
    DataValue analysis,
  ) async {
    try {
      // 1. AI处理
      final processResult = await _aiProcessor.processData(
        value,
        'data_enhancement',
        config: {'analysis': analysis},
      );
      
      // 2. 存储增强数据
      if (processResult.success) {
        await _localStorage.write(
          '${key}_enhanced',
          processResult.result,
        );
      }
      
      // 3. 更新元数据
      await _updateMetadata(key, analysis, processResult);
    } catch (e) {
      print('Failed to process valuable data $key: $e');
    }
  }
  
  /// 更新元数据
  Future<void> _updateMetadata(
    String key,
    DataValue analysis,
    AIProcessResult processResult,
  ) async {
    final metadata = {
      'valueScore': analysis.score,
      'metrics': analysis.metrics,
      'fingerprint': analysis.fingerprint,
      'processedAt': DateTime.now().toIso8601String(),
      'enhancementResult': processResult.success,
    };
    
    await _localStorage.write('${key}_metadata', metadata);
  }
  
  /// 构建数据上下文
  Future<DataContext> _buildDataContext(String key) async {
    final accessCount = await _getAccessCount(key);
    final relatedData = await _getRelatedData(key);
    
    return DataContext(
      timestamp: DateTime.now(),
      accessCount: accessCount,
      relatedData: relatedData,
    );
  }
  
  /// 获取访问次数
  Future<int> _getAccessCount(String key) async {
    try {
      final metadata = await _localStorage.read<Map<String, dynamic>>(
        '${key}_metadata',
      );
      return metadata?['accessCount'] ?? 0;
    } catch (e) {
      return 0;
    }
  }
  
  /// 获取相关数据
  Future<List<dynamic>> _getRelatedData(String key) async {
    // TODO: 实现获取相关数据的逻辑
    return [];
  }
  
  /// 释放资源
  void dispose() {
    _syncStatusController.close();
  }
}

/// 同步配置
class EdgeSyncConfig {
  /// 同步间隔
  final Duration syncInterval;
  
  /// 重试次数
  final int maxRetries;
  
  /// 批量大小
  final int batchSize;
  
  EdgeSyncConfig({
    this.syncInterval = const Duration(minutes: 15),
    this.maxRetries = 3,
    this.batchSize = 100,
  });
}

/// 存储策略
class StoragePolicy {
  /// 确定存储策略
  StorageStrategy determineStrategy(DataValue value) {
    if (value.score >= 0.8) {
      // 高价值数据：全量存储
      return StorageStrategy(
        useLocalStorage: true,
        useRemoteStorage: true,
        useMCP: true,
        useOSS: true,
        useDB: true,
      );
    } else if (value.score >= 0.5) {
      // 中等价值数据：本地+选择性远程
      return StorageStrategy(
        useLocalStorage: true,
        useRemoteStorage: true,
        useMCP: true,
        useOSS: false,
        useDB: true,
      );
    } else {
      // 低价值数据：仅本地
      return StorageStrategy(
        useLocalStorage: true,
        useRemoteStorage: false,
        useMCP: false,
        useOSS: false,
        useDB: false,
      );
    }
  }
}

/// 存储策略
class StorageStrategy {
  final bool useLocalStorage;
  final bool useRemoteStorage;
  final bool useMCP;
  final bool useOSS;
  final bool useDB;
  
  StorageStrategy({
    required this.useLocalStorage,
    required this.useRemoteStorage,
    required this.useMCP,
    required this.useOSS,
    required this.useDB,
  });
}

/// 同步状态
enum SyncState {
  idle,
  syncing,
  completed,
  error,
}

/// 同步状态
class SyncStatus {
  final SyncState state;
  final DateTime? lastSyncTime;
  final String? error;
  
  SyncStatus({
    required this.state,
    this.lastSyncTime,
    this.error,
  });
}

/// 同步目标
enum SyncTarget {
  mcp,
  oss,
  db,
}

/// 待同步项
class PendingSyncItem {
  final String key;
  final dynamic value;
  final SyncTarget target;
  final double priority;
  
  PendingSyncItem({
    required this.key,
    required this.value,
    required this.target,
    required this.priority,
  });
} 