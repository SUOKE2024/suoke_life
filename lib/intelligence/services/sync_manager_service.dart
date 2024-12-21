class SyncManagerService extends GetxService {
  final DataStorageService _storageService;
  final SecurityManagerService _securityManager;
  final EventTrackingService _eventTracking;
  
  // 同步配置
  static const Map<String, Duration> _syncIntervals = {
    'chat': Duration(minutes: 5),
    'settings': Duration(minutes: 15),
    'preferences': Duration(hours: 1),
  };
  
  // 同步状态
  final Map<String, DateTime> _lastSyncTime = {};
  final Map<String, bool> _syncInProgress = {};
  
  SyncManagerService({
    required DataStorageService storageService,
    required SecurityManagerService securityManager,
    required EventTrackingService eventTracking,
  })  : _storageService = storageService,
        _securityManager = securityManager,
        _eventTracking = eventTracking {
    _startPeriodicSync();
  }

  Future<void> sync(String dataType, {bool force = false}) async {
    if (_syncInProgress[dataType] == true) return;
    
    try {
      _syncInProgress[dataType] = true;
      
      // 检查是否需要同步
      if (!force && !_shouldSync(dataType)) return;
      
      // 获取本地数据
      final localData = await _getLocalData(dataType);
      
      // 加密数据
      final encryptedData = await _securityManager.encryptData(
        jsonEncode(localData)
      );
      
      // 上传数据
      await _uploadData(dataType, encryptedData);
      
      // 更新同步时间
      _lastSyncTime[dataType] = DateTime.now();
      
      // 记录同步事件
      await _trackSyncEvent(dataType, 'success');
    } catch (e) {
      await _trackSyncEvent(dataType, 'error', error: e);
      rethrow;
    } finally {
      _syncInProgress[dataType] = false;
    }
  }

  Future<Map<String, dynamic>> _getLocalData(String dataType) async {
    switch (dataType) {
      case 'chat':
        return await _storageService.getChatData();
      case 'settings':
        return await _storageService.getSettings();
      case 'preferences':
        return await _storageService.getPreferences();
      default:
        throw AIException(
          '未知的数据类型',
          code: 'UNKNOWN_DATA_TYPE',
        );
    }
  }

  Future<void> _uploadData(String dataType, String encryptedData) async {
    // TODO: 实现数据上传
  }

  bool _shouldSync(String dataType) {
    final lastSync = _lastSyncTime[dataType];
    if (lastSync == null) return true;
    
    final interval = _syncIntervals[dataType];
    if (interval == null) return false;
    
    return DateTime.now().difference(lastSync) > interval;
  }

  Future<void> _trackSyncEvent(
    String dataType,
    String status, {
    dynamic error,
  }) async {
    await _eventTracking.trackEvent(AIEvent(
      id: 'sync_${DateTime.now().millisecondsSinceEpoch}',
      userId: 'system',
      assistantName: 'system',
      type: AIEventType.sync,
      data: {
        'type': dataType,
        'status': status,
        'error': error?.toString(),
      },
    ));
  }

  void _startPeriodicSync() {
    Timer.periodic(Duration(minutes: 15), (_) async {
      for (final dataType in _syncIntervals.keys) {
        await sync(dataType);
      }
    });
  }
} 