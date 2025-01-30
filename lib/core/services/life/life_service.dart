import 'package:injectable/injectable.dart';
import '../../../core/storage/storage_service.dart';

@lazySingleton
class LifeService {
  final StorageService _storage;

  LifeService(this._storage);

  Future<void> init() async {
    await _storage.init();
  }

  Future<void> saveUserPreference(String key, dynamic value) async {
    await _storage.write(key, value);
  }

  Future<T?> getUserPreference<T>(String key) async {
    return await _storage.read<T>(key);
  }

  Future<void> clearUserPreferences() async {
    await _storage.clear();
  }
} 