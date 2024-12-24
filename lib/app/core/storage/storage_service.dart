import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite/sqflite.dart';
import '../database/database_helper.dart';
import 'package:get_storage/get_storage.dart';

class StorageService extends GetxService {
  late final GetStorage _box;
  
  Future<void> init() async {
    await GetStorage.init();
    _box = GetStorage();
  }

  Future<void> write(String key, dynamic value) => _box.write(key, value);
  dynamic read(String key) => _box.read(key);
  Future<void> remove(String key) => _box.remove(key);
  Future<void> clear() => _box.erase();
} 