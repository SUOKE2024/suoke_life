class DataSyncManager {
  static final instance = DataSyncManager._();
  DataSyncManager._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  final _networkMonitor = Get.find<NetworkMonitor>();
  
  final _syncQueue = <SyncOperation>[];
  final _pendingChanges = <String, List<DataChange>>{};
  final _syncStatus = Rx<SyncStatus>(SyncStatus.idle);
  
  Timer? _syncTimer;
  bool _isSyncing = false;

  static const _config = {
    'sync_interval': 300000,     // 同步间隔（5分钟）
    'batch_size': 100,           // 批量同步大小
    'conflict_strategy': 'server_wins', // 冲突解决策略
  };

  Future<void> initialize() async {
    // 加载待同步的更改
    await _loadPendingChanges();
    
    // 监听网络状态
    _networkMonitor.onlineStream.listen(_handleNetworkChange);
    
    // 启动定期同步
    _startPeriodicSync();
  }

  Future<void> _loadPendingChanges() async {
    final changes = await _storage.getObject<Map<String, dynamic>>(
      'pending_changes',
      (json) => json,
    );

    if (changes != null) {
      for (final entry in changes.entries) {
        _pendingChanges[entry.key] = (entry.value as List)
            .map((e) => DataChange.fromJson(e))
            .toList();
      }
    }
  }

  void _handleNetworkChange(bool isOnline) {
    if (isOnline && _pendingChanges.isNotEmpty) {
      syncNow();
    }
  }

  void _startPeriodicSync() {
    _syncTimer = Timer.periodic(
      Duration(milliseconds: _config['sync_interval']!),
      (_) => syncNow(),
    );
  }

  Future<void> syncNow() async {
    if (_isSyncing || !_networkMonitor.isOnline) return;

    _isSyncing = true;
    _syncStatus.value = SyncStatus.syncing;
    
    try {
      // 处理所有待同步的更改
      for (final entityType in _pendingChanges.keys) {
        await _syncEntityChanges(entityType);
      }
      
      _syncStatus.value = SyncStatus.completed;
      _eventBus.fire(SyncCompletedEvent());
    } catch (e) {
      _syncStatus.value = SyncStatus.error;
      _eventBus.fire(SyncFailedEvent(error: e));
    } finally {
      _isSyncing = false;
    }
  }

  Future<void> _syncEntityChanges(String entityType) async {
    final changes = _pendingChanges[entityType] ?? [];
    if (changes.isEmpty) return;

    // 按批次处理更改
    for (var i = 0; i < changes.length; i += _config['batch_size']!) {
      final batch = changes.skip(i).take(_config['batch_size']!).toList();
      await _processBatch(entityType, batch);
    }
  }

  Future<void> _processBatch(String entityType, List<DataChange> batch) async {
    try {
      final apiClient = Get.find<ApiClient>();
      final response = await apiClient.post(
        '/api/sync/$entityType',
        data: {
          'changes': batch.map((c) => c.toJson()).toList(),
          'strategy': _config['conflict_strategy'],
        },
      );

      // 处理服务器响应
      final serverChanges = (response['changes'] as List)
          .map((e) => DataChange.fromJson(e))
          .toList();

      // 应用服务器更改
      await _applyServerChanges(entityType, serverChanges);
      
      // 移除已同步的更改
      _pendingChanges[entityType]?.removeWhere(
        (change) => batch.any((b) => b.id == change.id),
      );
      
      await _savePendingChanges();
    } catch (e) {
      LoggerManager.instance.error('Sync failed for $entityType', e);
      rethrow;
    }
  }

  Future<void> _applyServerChanges(
    String entityType,
    List<DataChange> changes,
  ) async {
    final repository = Get.find<DataRepository>();
    for (final change in changes) {
      await repository.applyChange(entityType, change);
    }
  }

  Future<void> trackChange(String entityType, DataChange change) async {
    _pendingChanges.putIfAbsent(entityType, () => []).add(change);
    await _savePendingChanges();
    
    // 如果是在线状态，立即触发同步
    if (_networkMonitor.isOnline) {
      syncNow();
    }
  }

  Future<void> _savePendingChanges() async {
    final changes = <String, dynamic>{};
    for (final entry in _pendingChanges.entries) {
      changes[entry.key] = entry.value.map((e) => e.toJson()).toList();
    }
    await _storage.setObject('pending_changes', changes);
  }

  void dispose() {
    _syncTimer?.cancel();
    _syncQueue.clear();
    _pendingChanges.clear();
  }
}

class DataChange {
  final String id;
  final String entityId;
  final ChangeType type;
  final Map<String, dynamic> data;
  final DateTime timestamp;
  final String? deviceId;

  DataChange({
    required this.id,
    required this.entityId,
    required this.type,
    required this.data,
    required this.timestamp,
    this.deviceId,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'entityId': entityId,
    'type': type.toString(),
    'data': data,
    'timestamp': timestamp.toIso8601String(),
    'deviceId': deviceId,
  };

  factory DataChange.fromJson(Map<String, dynamic> json) => DataChange(
    id: json['id'],
    entityId: json['entityId'],
    type: ChangeType.values.byName(json['type']),
    data: Map<String, dynamic>.from(json['data']),
    timestamp: DateTime.parse(json['timestamp']),
    deviceId: json['deviceId'],
  );
}

enum ChangeType {
  create,
  update,
  delete,
  merge,
}

enum SyncStatus {
  idle,
  syncing,
  completed,
  error,
}

class SyncCompletedEvent extends AppEvent {}

class SyncFailedEvent extends AppEvent {
  final dynamic error;
  SyncFailedEvent({required this.error});
} 