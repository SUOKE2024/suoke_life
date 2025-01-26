import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:suoke_life/app/core/utils/timeago_utils.dart';

class TestHelper {
  static Future<void> initializeTest() async {
    TestWidgetsFlutterBinding.ensureInitialized();
    SharedPreferences.setMockInitialValues({});

    // 初始化 SQLite
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;

    // 初始化 timeago
    TimeagoUtils.init();

    // 初始化 GetX
    Get.testMode = true;
    Get.reset();
  }

  static void clearTest() {
    Get.reset();
  }
}
