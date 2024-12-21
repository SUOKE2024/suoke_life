import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

class StorageQuotaService {
  static const int _maxStorageBytes = 1024 * 1024 * 1024; // 1GB
  static const String _usedStorageKey = 'used_storage_bytes';

  final SharedPreferences _prefs;

  StorageQuotaService(this._prefs);

  Future<int> getUsedStorage() async {
    return _prefs.getInt(_usedStorageKey) ?? 0;
  }

  Future<int> getRemainingStorage() async {
    final usedStorage = await getUsedStorage();
    return _maxStorageBytes - usedStorage;
  }

  Future<bool> checkStorageAvailable(int bytes) async {
    final remaining = await getRemainingStorage();
    return remaining >= bytes;
  }

  Future<void> updateUsedStorage(int deltaBytes) async {
    final currentUsed = await getUsedStorage();
    await _prefs.setInt(_usedStorageKey, currentUsed + deltaBytes);
  }

  Future<void> cleanupOldFiles({Duration? maxAge}) async {
    final dir = await getApplicationDocumentsDirectory();
    final files = dir.listSync(recursive: true);
    
    for (var entity in files) {
      if (entity is File) {
        final stat = await entity.stat();
        final age = DateTime.now().difference(stat.modified);
        
        if (maxAge != null && age > maxAge) {
          final size = await entity.length();
          await entity.delete();
          await updateUsedStorage(-size);
        }
      }
    }
  }
} 