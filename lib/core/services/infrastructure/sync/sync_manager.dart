import 'package:get/get.dart';
import '../storage/storage_service.dart';
import '../network/network_service.dart';

class SyncManager {
  final StorageService _storage;
  final NetworkService _network;
  final _syncQueue = <SyncTask>[];
  
  bool _isSyncing = false;

  SyncManager(this._storage, this._network);

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
      if (task.retryCount < 3) {
        task.retryCount++;
        _syncQueue.add(task);
      }
    }

    await _processQueue();
  }
}

class SyncTask {
  final SyncType type;
  final Map<String, dynamic> data;
  final SyncPriority priority;
  int retryCount = 0;

  SyncTask({
    required this.type,
    required this.data,
    required this.priority,
  });

  Future<void> execute() async {
    // 实现同步逻辑
  }
}

enum SyncType {
  userProfile,
  chatMessage,
  lifeRecord,
  healthData,
}

enum SyncPriority {
  low,
  medium,
  high,
} 