import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:suoke_app/app/core/database/database_service.dart';

void main() {
  late DatabaseService databaseService;

  setUpAll(() {
    // 初始化 FFI
    sqfliteFfiInit();
    // 设置数据库工厂
    databaseFactory = databaseFactoryFfi;
  });

  setUp(() {
    databaseService = DatabaseService();
  });

  tearDown(() async {
    // 清理测试数据库
    final db = await databaseService.database;
    await db.close();
  });

  group('Database Service Tests', () {
    test('should initialize database', () async {
      final db = await databaseService.database;
      expect(db, isNotNull);
      expect(db.isOpen, true);
    });
  });
} 