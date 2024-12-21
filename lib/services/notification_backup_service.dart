import '../data/remote/mysql/knowledge_database.dart';
import '../data/remote/s3/s3_storage.dart';
import 'dart:convert';
import 'dart:io';
import 'package:archive/archive.dart';

class NotificationBackupService {
  final KnowledgeDatabase _knowledgeDb;
  final S3Storage _s3Storage;

  NotificationBackupService(this._knowledgeDb, this._s3Storage);

  // 创建备份
  Future<BackupResult> createBackup({
    required String name,
    String? description,
  }) async {
    // 1. 导出数据
    final data = await _exportData();
    
    // 2. 压缩数据
    final compressed = await _compressData(data);
    
    // 3. 上传到S3
    final key = _generateBackupKey(name);
    await _s3Storage.putObject(
      bucket: 'notifications-backup',
      key: key,
      data: compressed,
    );
    
    // 4. 记录备份
    final backupId = await _recordBackup(name, description, key);

    return BackupResult(
      id: backupId,
      name: name,
      size: compressed.length,
    );
  }

  // 恢复备份
  Future<RestoreResult> restoreBackup(String backupId) async {
    // 1. 获取备份信息
    final backup = await _getBackup(backupId);
    
    // 2. 从S3下载
    final compressed = await _s3Storage.getObject(
      bucket: 'notifications-backup',
      key: backup.key,
    );
    
    // 3. 解压数据
    final data = await _decompressData(compressed);
    
    // 4. 恢复数据
    final restored = await _restoreData(data);

    return RestoreResult(
      success: true,
      restoredCount: restored,
    );
  }

  // 导出数据
  Future<Map<String, dynamic>> _exportData() async {
    // 1. 导出通知数据
    final notifications = await _knowledgeDb._conn.query(
      'SELECT * FROM notifications',
    );

    // 2. 导出配置数据
    final settings = await _knowledgeDb._conn.query(
      'SELECT * FROM notification_settings',
    );

    // 3. 导出模板数据
    final templates = await _knowledgeDb._conn.query(
      'SELECT * FROM notification_templates',
    );

    return {
      'version': '1.0',
      'timestamp': DateTime.now().toIso8601String(),
      'notifications': notifications.map((r) => r.fields).toList(),
      'settings': settings.map((r) => r.fields).toList(),
      'templates': templates.map((r) => r.fields).toList(),
    };
  }

  // 压缩数据
  Future<List<int>> _compressData(Map<String, dynamic> data) async {
    final jsonStr = jsonEncode(data);
    final bytes = utf8.encode(jsonStr);
    return GZipEncoder().encode(bytes)!;
  }

  // 解压数据
  Future<Map<String, dynamic>> _decompressData(List<int> compressed) async {
    final bytes = GZipDecoder().decodeBytes(compressed);
    final jsonStr = utf8.decode(bytes);
    return jsonDecode(jsonStr);
  }

  // 生成备份键
  String _generateBackupKey(String name) {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    return 'backups/$name-$timestamp.gz';
  }

  // 记录备份
  Future<String> _recordBackup(
    String name,
    String? description,
    String key,
  ) async {
    final backupId = DateTime.now().millisecondsSinceEpoch.toString();
    
    await _knowledgeDb._conn.query('''
      INSERT INTO notification_backups (
        id, name, description, file_key,
        created_at
      ) VALUES (?, ?, ?, ?, NOW())
    ''', [backupId, name, description, key]);

    return backupId;
  }

  // 获取备份信息
  Future<BackupInfo> _getBackup(String backupId) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM notification_backups
      WHERE id = ?
    ''', [backupId]);

    if (results.isEmpty) {
      throw Exception('Backup not found: $backupId');
    }

    return BackupInfo.fromJson(results.first.fields);
  }

  // 恢复数据
  Future<int> _restoreData(Map<String, dynamic> data) async {
    // TODO: 实现数据恢复逻辑
    return 0;
  }
}

class BackupResult {
  final String id;
  final String name;
  final int size;

  BackupResult({
    required this.id,
    required this.name,
    required this.size,
  });
}

class RestoreResult {
  final bool success;
  final int restoredCount;

  RestoreResult({
    required this.success,
    required this.restoredCount,
  });
}

class BackupInfo {
  final String id;
  final String name;
  final String? description;
  final String key;
  final DateTime createdAt;

  BackupInfo({
    required this.id,
    required this.name,
    this.description,
    required this.key,
    required this.createdAt,
  });

  factory BackupInfo.fromJson(Map<String, dynamic> json) {
    return BackupInfo(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      key: json['file_key'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
} 