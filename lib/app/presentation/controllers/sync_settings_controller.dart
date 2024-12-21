import 'package:get/get.dart';
import '../../core/services/storage_service.dart';
import '../../core/constants/storage_keys.dart';

class SyncSettingsController extends GetxController {
  final StorageService storageService;

  SyncSettingsController({required this.storageService});

  final syncRange = 7.obs;
  final autoSync = false.obs;

  @override
  void onInit() {
    super.onInit();
    loadSettings();
  }

  Future<void> loadSettings() async {
    syncRange.value = storageService.getInt(StorageKeys.syncRange) ?? 7;
    autoSync.value = storageService.getBool(StorageKeys.autoSync) ?? false;
  }

  Future<void> setSyncRange(int days) async {
    await storageService.setInt(StorageKeys.syncRange, days);
    syncRange.value = days;
  }

  Future<void> setAutoSync(bool enabled) async {
    await storageService.setBool(StorageKeys.autoSync, enabled);
    autoSync.value = enabled;
  }
} 