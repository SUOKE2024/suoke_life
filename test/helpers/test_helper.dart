import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:sqflite/sqflite.dart';

class TestHelper {
  static void setupTest() {
    Get.reset();
    
    // 初始化 FFI
    sqfliteFfiInit();
    // 设置数据库工厂
    databaseFactory = databaseFactoryFfi;
  }

  static void clearTest() {
    Get.reset();
  }
} 