import '../database/database_service.dart';
import '../network/network_service.dart';
import '../security/anonymizer_service.dart';

class SyncService {
  final DatabaseService _db;
  final NetworkService _network;
  final AnonymizerService _anonymizer;
  
  final _syncQueue = <SyncTask>[];
  bool _isSyncing = false;

  SyncService(this._db, this._network, this._anonymizer);

  Future<void> syncUserData(String userId) async {
    // 1. 获取本地数据
    final userData = await _db.getUserData(userId);
    if (userData == null) return;

    // 2. 数据脱敏
    final anonymizedData = _anonymizer.anonymizeUserData(userData);

    // 3. 添加到同步队列
    _syncQueue.add(SyncTask(
      type: SyncType.userData,
      data: anonymizedData,
      priority: SyncPriority.high,
    ));

    // 4. 处理同步队列
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
    
    // 按优先级排序
    _syncQueue.sort((a, b) => b.priority.index.compareTo(a.priority.index));
    
    while (_syncQueue.isNotEmpty) {
      final task = _syncQueue.removeAt(0);
      try {
        await _syncTask(task);
      } catch (e) {
        // 失败后重新加入队列
        if (task.retryCount < 3) {
          task.retryCount++;
          _syncQueue.add(task);
        }
      }
    }

    _isSyncing = false;
  }

  Future<void> _syncTask(SyncTask task) async {
    switch (task.type) {
      case SyncType.userData:
        await _network.post('/sync/user-data', task.data);
        break;
      case SyncType.healthRecord:
        await _network.post('/sync/health-record', task.data);
        break;
      // ... 其他同步类型
    }
  }
}

enum SyncType {
  userData,
  healthRecord,
  behaviorData,
  preferences,
}

enum SyncPriority {
  low,
  medium,
  high,
}

class SyncTask {
  final SyncType type;
  final Map<String, dynamic> data;
  final SyncPriority priority;
  int retryCount = 0;

  SyncTask({
    required this.type,
    required this.data,
    this.priority = SyncPriority.medium,
  });
} 