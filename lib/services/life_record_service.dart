import 'dart:io';
import 'package:get/get.dart';
import 'package:sqflite/sqflite.dart';
import '../data/local/database/database_helper.dart';
import '../models/life_record.dart';

class LifeRecordService extends GetxService {
  final _dbHelper = DatabaseHelper();

  // 获取所有记录
  Future<List<LifeRecord>> getAllRecords() async {
    final db = await _dbHelper.database;
    final records = await db.query(
      'life_records',
      orderBy: 'time DESC',
    );
    
    return records.map((r) => LifeRecord.fromMap(r)).toList();
  }

  // 添加记录
  Future<void> addRecord({
    required String content,
    List<String> tags = const [],
    List<File> images = const [],
    String? location,
  }) async {
    final db = await _dbHelper.database;
    
    final record = {
      'id': DateTime.now().millisecondsSinceEpoch.toString(),
      'content': content,
      'time': DateTime.now().toIso8601String(),
      'location': location,
      'images': images.map((f) => f.path).join(','),
    };

    await db.insert('life_records', record);
  }

  // 按日期范围搜索
  Future<List<LifeRecord>> searchByDateRange(DateTime start, DateTime end) async {
    final db = await _dbHelper.database;
    final records = await db.query(
      'life_records',
      where: 'time BETWEEN ? AND ?',
      whereArgs: [
        start.toIso8601String(),
        end.toIso8601String(),
      ],
      orderBy: 'time DESC',
    );
    
    return records.map((r) => LifeRecord.fromMap(r)).toList();
  }

  // 按关键词搜索
  Future<List<LifeRecord>> searchByKeyword(String keyword) async {
    if (keyword.isEmpty) return [];
    
    final db = await _dbHelper.database;
    final records = await db.query(
      'life_records',
      where: 'content LIKE ?',
      whereArgs: ['%$keyword%'],
      orderBy: 'time DESC',
    );
    
    return records.map((r) => LifeRecord.fromMap(r)).toList();
  }
} 