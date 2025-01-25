import 'package:get/get.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_app/app/core/services/storage/storage_service.dart';

class MockStorageService extends GetxService with Mock implements StorageService {
  final Map<String, dynamic> _storage = {};

  @override
  Future<StorageService> init() async {
    // Mock initialization
    return this;
  }

  @override
  Future<void> dispose() async {
    _storage.clear();
  }

  @override
  Future<void> setString(String key, String value) async {
    _storage[key] = value;
  }

  @override
  String? getString(String key) {
    return _storage[key] as String?;
  }

  @override
  Future<void> setBool(String key, bool value) async {
    _storage[key] = value;
  }

  @override
  bool? getBool(String key) {
    return _storage[key] as bool?;
  }

  @override
  Future<bool> remove(String key) async {
    final existed = _storage.containsKey(key);
    _storage.remove(key);
    return existed;
  }

  @override
  Future<bool> clear() async {
    _storage.clear();
    return true;
  }

  @override
  void onInit() {
    super.onInit();
  }

  @override
  void onReady() {
    super.onReady();
  }

  @override
  void onClose() {
    super.onClose();
  }
} 