import '../logger/app_logger.dart';
import 'secure_storage.dart';

class SecureStorageImpl implements SecureStorage {
  final FlutterSecureStorage _storage;
  final AppLogger _logger;

  SecureStorageImpl(this._logger) : _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true,
    ),
    iOptions: IOSOptions(
      accessibility: KeychainAccessibility.first_unlock,
    ),
  );

  @override
  Future<String?> read(String key) async {
    try {
      return await _storage.read(key: key);
    } catch (e, stack) {
      _logger.error('Failed to read from secure storage: $key', e, stack);
      return null;
    }
  }

  @override 
  Future<void> write(String key, String value) async {
    try {
      await _storage.write(key: key, value: value);
    } catch (e, stack) {
      _logger.error('Failed to write to secure storage: $key', e, stack);
      rethrow;
    }
  }

  @override
  Future<void> delete(String key) async {
    try {
      await _storage.delete(key: key);
    } catch (e, stack) {
      _logger.error('Failed to delete from secure storage: $key', e, stack);
      rethrow;
    }
  }

  @override
  Future<void> clear() async {
    try {
      await _storage.deleteAll();
    } catch (e, stack) {
      _logger.error('Failed to clear secure storage', e, stack);
      rethrow;
    }
  }
} 