import 'package:flutter/widgets.dart';
import 'package:get_it/get_it.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:suoke_life_app_app_app/app/core/di/injection.dart';

class TestConfig {
  static Future<void> init() async {
    WidgetsFlutterBinding.ensureInitialized();
    
    // 初始化 sqflite_ffi
    sqfliteFfiInit();
    
    // 重置 GetIt
    GetIt.instance.reset();
    
    // 配置依赖
    await configureDependencies();
  }
} 