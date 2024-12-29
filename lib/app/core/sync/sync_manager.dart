class SyncManager {
  final StorageService _storage;
  final NetworkService _network;
  final _syncQueue = <SyncTask>[];
  
  bool _isSyncing = false;

  Future<void> scheduleSync(SyncTask task) async {
    _syncQueue.add(task);
    if (!_isSyncing) {
      await _processQueue();
    }
  }

  Future<void> _processQueue() async {
    if (_syncQueue.isEmpty) {
      _isSyncing = false;
      return;
    }

    _isSyncing = true;
    final task = _syncQueue.removeAt(0);

    try {
      await task.execute();
    } catch (e) {
      // 失败后重新加入队列
      _syncQueue.add(task);
    }

    await _processQueue();
  }
} 