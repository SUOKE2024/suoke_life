import 'package:get/get.dart';
import '../app/core/services/storage_service.dart';
import '../app/core/constants/storage_keys.dart';

class SettingsService extends GetxService {
  final _storage = Get.find<StorageService>();
  
  Future<void> saveThemeMode(ThemeMode mode) async {
    await _storage.setString(StorageKeys.themeMode, mode.toString());
  }
  
  ThemeMode getThemeMode() {
    final value = _storage.getString(StorageKeys.themeMode);
    return value != null ? ThemeMode.values.byName(value) : ThemeMode.system;
  }
} 