import 'dart:io';

import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class DataStorageService {
  static Database? _database;
  static const String databaseName = 'suoke_life.db';

  Future<Database> get database async {
    _database ??= await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final documentsDirectory = await getApplicationDocumentsDirectory();
    final path = join(documentsDirectory.path, databaseName);

    return await openDatabase(
      path,
      version: 1,
      onCreate: _createTables,
    );
  }

  Future<void> _createTables(Database db, int version) async {
    // 健康数据表
    await db.execute('''
      CREATE TABLE health_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        type TEXT NOT NULL,
        data TEXT NOT NULL,
        metadata TEXT
      )
    ''');

    // 声纹数据表
    await db.execute('''
      CREATE TABLE voice_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        file_path TEXT NOT NULL,
        duration INTEGER,
        metadata TEXT
      )
    ''');

    // 视频数据表
    await db.execute('''
      CREATE TABLE video_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        file_path TEXT NOT NULL,
        duration INTEGER,
        metadata TEXT
      )
    ''');
  }

  // 健康数据存储
  Future<int> saveHealthData(Map<String, dynamic> data) async {
    final db = await database;
    return await db.insert('health_data', {
      'timestamp': DateTime.now().toIso8601String(),
      'type': data['type'],
      'data': data['data'].toString(),
      'metadata': data['metadata']?.toString(),
    });
  }

  // 声纹数据存储
  Future<int> saveVoiceData(File file, Map<String, dynamic> metadata) async {
    final db = await database;
    final savedFile = await _saveFile(file, 'voice');
    
    return await db.insert('voice_data', {
      'timestamp': DateTime.now().toIso8601String(),
      'file_path': savedFile.path,
      'duration': metadata['duration'],
      'metadata': metadata.toString(),
    });
  }

  // 视频数据存储
  Future<int> saveVideoData(File file, Map<String, dynamic> metadata) async {
    final db = await database;
    final savedFile = await _saveFile(file, 'video');
    
    return await db.insert('video_data', {
      'timestamp': DateTime.now().toIso8601String(),
      'file_path': savedFile.path,
      'duration': metadata['duration'],
      'metadata': metadata.toString(),
    });
  }

  // 获取健康数据历史
  Future<List<Map<String, dynamic>>> getHealthDataHistory({
    String? type,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final db = await database;
    String query = 'SELECT * FROM health_data';
    List<String> conditions = [];
    List<dynamic> arguments = [];

    if (type != null) {
      conditions.add('type = ?');
      arguments.add(type);
    }

    if (startDate != null) {
      conditions.add('timestamp >= ?');
      arguments.add(startDate.toIso8601String());
    }

    if (endDate != null) {
      conditions.add('timestamp <= ?');
      arguments.add(endDate.toIso8601String());
    }

    if (conditions.isNotEmpty) {
      query += ' WHERE ' + conditions.join(' AND ');
    }

    query += ' ORDER BY timestamp DESC';
    return await db.rawQuery(query, arguments);
  }

  // 获取声纹数据历史
  Future<List<Map<String, dynamic>>> getVoiceDataHistory({
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final db = await database;
    String query = 'SELECT * FROM voice_data';
    List<String> conditions = [];
    List<dynamic> arguments = [];

    if (startDate != null) {
      conditions.add('timestamp >= ?');
      arguments.add(startDate.toIso8601String());
    }

    if (endDate != null) {
      conditions.add('timestamp <= ?');
      arguments.add(endDate.toIso8601String());
    }

    if (conditions.isNotEmpty) {
      query += ' WHERE ' + conditions.join(' AND ');
    }

    query += ' ORDER BY timestamp DESC';
    return await db.rawQuery(query, arguments);
  }

  // 获取视频数据历史
  Future<List<Map<String, dynamic>>> getVideoDataHistory({
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final db = await database;
    String query = 'SELECT * FROM video_data';
    List<String> conditions = [];
    List<dynamic> arguments = [];

    if (startDate != null) {
      conditions.add('timestamp >= ?');
      arguments.add(startDate.toIso8601String());
    }

    if (endDate != null) {
      conditions.add('timestamp <= ?');
      arguments.add(endDate.toIso8601String());
    }

    if (conditions.isNotEmpty) {
      query += ' WHERE ' + conditions.join(' AND ');
    }

    query += ' ORDER BY timestamp DESC';
    return await db.rawQuery(query, arguments);
  }

  // 文件存储
  Future<File> _saveFile(File sourceFile, String type) async {
    final directory = await getApplicationDocumentsDirectory();
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final extension = sourceFile.path.split('.').last;
    final fileName = '${type}_$timestamp.$extension';
    final targetPath = join(directory.path, type, fileName);

    // 确保目标目录存在
    final targetDir = Directory(join(directory.path, type));
    if (!await targetDir.exists()) {
      await targetDir.create(recursive: true);
    }

    // 复制文件
    return await sourceFile.copy(targetPath);
  }

  // 获取临时目录
  Future<Directory> getTemporaryDirectory() async {
    return await getTemporaryDirectory();
  }

  // 清理过期数据
  Future<void> cleanupExpiredData(Duration maxAge) async {
    final db = await database;
    final cutoffDate = DateTime.now().subtract(maxAge).toIso8601String();

    // 删除过期的健康数据
    await db.delete(
      'health_data',
      where: 'timestamp < ?',
      whereArgs: [cutoffDate],
    );

    // 删除过期的声纹数据（同时删除文件）
    final expiredVoiceData = await db.query(
      'voice_data',
      where: 'timestamp < ?',
      whereArgs: [cutoffDate],
    );

    for (var data in expiredVoiceData) {
      final filePath = data['file_path'] as String;
      final file = File(filePath);
      if (await file.exists()) {
        await file.delete();
      }
    }

    await db.delete(
      'voice_data',
      where: 'timestamp < ?',
      whereArgs: [cutoffDate],
    );

    // 删除过期的视频数据（同时删除文件）
    final expiredVideoData = await db.query(
      'video_data',
      where: 'timestamp < ?',
      whereArgs: [cutoffDate],
    );

    for (var data in expiredVideoData) {
      final filePath = data['file_path'] as String;
      final file = File(filePath);
      if (await file.exists()) {
        await file.delete();
      }
    }

    await db.delete(
      'video_data',
      where: 'timestamp < ?',
      whereArgs: [cutoffDate],
    );
  }
} 