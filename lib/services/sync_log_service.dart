import 'package:get/get.dart';
import 'package:hive/hive.dart';
import 'package:uuid/uuid.dart';
import 'package:suoke_life/data/models/sync_log.dart';
import 'package:suoke_life/data/models/sync_conflict.dart';

class SyncLogService extends GetxService {
  late Box<SyncLog> _logBox;
  late Box<SyncConflict> _conflictBox;
  final _uuid = Uuid();

  @override
  Future<void> onInit() async {
    super.onInit();
    await _initHive();
  }

  Future<void> _initHive() async {
    _logBox = await Hive.openBox<SyncLog>('sync_logs');
    _conflictBox = await Hive.openBox<SyncConflict>('sync_conflicts');
  }

  // 记录同步日志
  Future<void> logSync({
    required String type,
    required bool success,
    String? error,
    Map<String, dynamic>? details,
  }) async {
    final log = SyncLog(
      id: _uuid.v4(),
      time: DateTime.now(),
      type: type,
      success: success,
      error: error,
      details: details,
    );
    await _logBox.add(log);
  }

  // 记录同步冲突
  Future<void> logConflict({
    required String type,
    required DateTime localTime,
    required DateTime serverTime,
    required Map<String, dynamic> localData,
    required Map<String, dynamic> serverData,
  }) async {
    final conflict = SyncConflict(
      id: _uuid.v4(),
      type: type,
      localTime: localTime,
      serverTime: serverTime,
      localData: localData,
      serverData: serverData,
    );
    await _conflictBox.add(conflict);
  }

  // 获取同步日志
  List<SyncLog> getLogs({int limit = 50}) {
    final logs = _logBox.values.toList();
    logs.sort((a, b) => b.time.compareTo(a.time));
    return logs.take(limit).toList();
  }

  // 获取未解决的冲突
  List<SyncConflict> getUnresolvedConflicts() {
    return _conflictBox.values
        .where((conflict) => !conflict.resolved)
        .toList();
  }

  // 解决冲突
  Future<void> resolveConflict(
    String id, {
    required String resolution,
  }) async {
    final conflict = _conflictBox.values
        .firstWhere((conflict) => conflict.id == id);
    
    final updatedConflict = conflict.copyWith(
      resolved: true,
      resolution: resolution,
    );
    
    final index = _conflictBox.values.toList()
        .indexWhere((conflict) => conflict.id == id);
    
    await _conflictBox.putAt(index, updatedConflict);
  }

  // 清理旧日志
  Future<void> cleanOldLogs({int keepDays = 30}) async {
    final cutoff = DateTime.now().subtract(Duration(days: keepDays));
    final oldLogs = _logBox.values
        .where((log) => log.time.isBefore(cutoff))
        .toList();
    
    for (final log in oldLogs) {
      await log.delete();
    }
  }

  // 清理已解决的冲突
  Future<void> cleanResolvedConflicts({int keepDays = 7}) async {
    final cutoff = DateTime.now().subtract(Duration(days: keepDays));
    final oldConflicts = _conflictBox.values
        .where((conflict) => 
          conflict.resolved && conflict.localTime.isBefore(cutoff))
        .toList();
    
    for (final conflict in oldConflicts) {
      await conflict.delete();
    }
  }
} 