import 'dart:convert';
import 'package:get/get.dart';
import '../core/database/database_helper.dart';
import '../data/models/sync_config.dart';
import '../data/models/sync_log.dart';
import '../data/models/sync_conflict.dart';

class SyncService extends GetxService {
  final _db = DatabaseHelper.instance;

  Future<SyncConfig?> getSyncConfig() async {
    final results = await _db.queryAll('sync_configs');
    if (results.isEmpty) return null;
    return SyncConfig.fromJson(results.first);
  }

  Future<void> saveSyncConfig(SyncConfig config) async {
    await _db.insert('sync_configs', config.toJson());
  }

  Future<void> logSync(SyncLog log) async {
    await _db.insert('sync_logs', log.toJson());
  }

  Future<void> saveSyncConflict(SyncConflict conflict) async {
    final data = conflict.toJson();
    data['local_data'] = jsonEncode(data['localData']);
    data['server_data'] = jsonEncode(data['serverData']);
    await _db.insert('sync_conflicts', data);
  }

  Future<List<SyncConflict>> getUnresolvedConflicts() async {
    final db = await _db.database;
    final results = await db.query(
      'sync_conflicts',
      where: 'resolved = ?',
      whereArgs: [0],
    );
    return results.map((map) {
      map['localData'] = jsonDecode(map['local_data']);
      map['serverData'] = jsonDecode(map['server_data']);
      return SyncConflict.fromJson(map);
    }).toList();
  }
} 