class SyncManager {
  static final instance = SyncManager._();
  SyncManager._();

  final _syncQueue = Queue<SyncTask>();
  final _syncInProgress = false.obs;
  final _lastSyncTime = Rxn<DateTime>();
  
  Timer? _syncTimer;
  final _eventBus = Get.find<EventBus>();

  Future<void> initialize() async {
    await _loadLastSyncTime();
    _startPeriodicSync();
  }

  Future<void> _loadLastSyncTime() async {
    final storage = Get.find<StorageManager>();
    final timestamp = await storage.get<int>('last_sync_time');
    if (timestamp != null) {
      _lastSyncTime.value = DateTime.fromMillisecondsSinceEpoch(timestamp);
    }
  }

  void _startPeriodicSync() {
    _syncTimer = Timer.periodic(const Duration(minutes: 15), (_) {
      scheduleSync();
    });
  }

  Future<void> scheduleSync({bool immediate = false}) async {
    if (immediate) {
      await _performSync();
    } else {
      _syncQueue.add(SyncTask());
      _processSyncQueue();
    }
  }

  Future<void> _processSyncQueue() async {
    if (_syncInProgress.value || _syncQueue.isEmpty) return;

    _syncInProgress.value = true;
    try {
      while (_syncQueue.isNotEmpty) {
        final task = _syncQueue.removeFirst();
        await _performSync(task);
      }
    } finally {
      _syncInProgress.value = false;
    }
  }

  Future<void> _performSync([SyncTask? task]) async {
    try {
      // 执行同步逻辑
      await _syncUserData();
      await _syncAppSettings();
      await _syncGameData();
      
      _lastSyncTime.value = DateTime.now();
      await _saveLastSyncTime();
      
      _eventBus.fire(SyncCompletedEvent());
    } catch (e) {
      _eventBus.fire(SyncFailedEvent(error: e));
      rethrow;
    }
  }

  Future<void> _saveLastSyncTime() async {
    final storage = Get.find<StorageManager>();
    await storage.set('last_sync_time', _lastSyncTime.value!.millisecondsSinceEpoch);
  }

  void dispose() {
    _syncTimer?.cancel();
    _syncQueue.clear();
  }
}

class SyncTask {
  final DateTime createdAt = DateTime.now();
  final String id = const Uuid().v4();
} 