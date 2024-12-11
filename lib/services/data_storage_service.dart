import 'dart:convert';

import 'package:sqflite/sqflite.dart';
import 'dart:io';

class DataStorageService {
  static Database? _database;
  static const String dbName = 'user_data.db';

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final documentsDirectory = await getApplicationDocumentsDirectory();
    final path = '${documentsDirectory.path}/$dbName';

    return await openDatabase(
      path,
      version: 1,
      onCreate: (Database db, int version) async {
        // 创建语音数据表
        await db.execute('''
          CREATE TABLE voice_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            timestamp TEXT,
            duration INTEGER,
            file_path TEXT
          )
        ''');

        // 创建视频数据表
        await db.execute('''
          CREATE TABLE video_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            timestamp TEXT,
            duration INTEGER,
            analysis_result TEXT
          )
        ''');

        // 创建用户数据表
        await db.execute('''
          CREATE TABLE user_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_type TEXT,
            content TEXT,
            timestamp TEXT,
            metadata TEXT
          )
        ''');
      },
    );
  }

  // 语音数据操作
  Future<int> saveVoiceRecord({
    required String content,
    required String filePath,
    required int duration,
  }) async {
    final db = await database;
    return await db.insert('voice_records', {
      'content': content,
      'timestamp': DateTime.now().toIso8601String(),
      'duration': duration,
      'file_path': filePath,
    });
  }

  Future<List<Map<String, dynamic>>> getVoiceRecords() async {
    final db = await database;
    return await db.query('voice_records', orderBy: 'timestamp DESC');
  }

  // 视频数据操作
  Future<int> saveVideoRecord({
    required String filePath,
    required int duration,
    required Map<String, dynamic> analysisResult,
  }) async {
    final db = await database;
    return await db.insert('video_records', {
      'file_path': filePath,
      'timestamp': DateTime.now().toIso8601String(),
      'duration': duration,
      'analysis_result': jsonEncode(analysisResult),
    });
  }

  Future<List<Map<String, dynamic>>> getVideoRecords() async {
    final db = await database;
    return await db.query('video_records', orderBy: 'timestamp DESC');
  }

  // 用户数据操作
  Future<int> saveUserData({
    required String dataType,
    required Map<String, dynamic> content,
    Map<String, dynamic>? metadata,
  }) async {
    final db = await database;
    return await db.insert('user_data', {
      'data_type': dataType,
      'content': jsonEncode(content),
      'timestamp': DateTime.now().toIso8601String(),
      'metadata': metadata != null ? jsonEncode(metadata) : null,
    });
  }

  Future<List<Map<String, dynamic>>> getUserData({
    String? dataType,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final db = await database;
    String whereClause = '';
    List<dynamic> whereArgs = [];

    if (dataType != null) {
      whereClause += 'data_type = ?';
      whereArgs.add(dataType);
    }

    if (startDate != null) {
      whereClause += whereClause.isEmpty ? 'timestamp >= ?' : ' AND timestamp >= ?';
      whereArgs.add(startDate.toIso8601String());
    }

    if (endDate != null) {
      whereClause += whereClause.isEmpty ? 'timestamp <= ?' : ' AND timestamp <= ?';
      whereArgs.add(endDate.toIso8601String());
    }

    return await db.query(
      'user_data',
      where: whereClause.isEmpty ? null : whereClause,
      whereArgs: whereArgs.isEmpty ? null : whereArgs,
      orderBy: 'timestamp DESC',
    );
  }

  // 文件管理
  Future<String> saveFile(File file, String directory) async {
    final documentsDirectory = await getApplicationDocumentsDirectory();
    final targetDirectory = Directory('${documentsDirectory.path}/$directory');
    
    if (!await targetDirectory.exists()) {
      await targetDirectory.create(recursive: true);
    }

    final String fileName = '${DateTime.now().millisecondsSinceEpoch}_${file.path.split('/').last}';
    final String targetPath = '${targetDirectory.path}/$fileName';
    
    await file.copy(targetPath);
    return targetPath;
  }

  Future<void> deleteFile(String filePath) async {
    final file = File(filePath);
    if (await file.exists()) {
      await file.delete();
    }
  }

  // 数据库清理
  Future<void> clearDatabase() async {
    final db = await database;
    await db.delete('voice_records');
    await db.delete('video_records');
    await db.delete('user_data');
  }

  Future<void> dispose() async {
    if (_database != null) {
      await _database!.close();
      _database = null;
    }
  }
} 