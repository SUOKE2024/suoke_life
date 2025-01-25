import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:path/path.dart' as path;
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:path_provider/path_provider.dart';

class TestConfig {
  static bool _initialized = false;

  static Future<void> init() async {
    if (_initialized) return;
    
    // 初始化 SQLite FFI
    sqfliteFfiInit();
    
    // 使用内存数据库配置
    final databaseFactory = databaseFactoryFfi;
    
    // 设置测试环境标志
    _initialized = true;
  }
  
  static Future<void> cleanup() async {
    // 清理测试资源
    _initialized = false;
  }
} 