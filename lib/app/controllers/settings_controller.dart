import 'package:get/get.dart';
import '../core/services/storage_service.dart';
import '../core/constants/storage_keys.dart';

class SettingsController extends GetxController {
  final _storage = Get.find<StorageService>();
  
  final fontSize = 16.0.obs;
  
  @override
  void onInit() {
    super.onInit();
    fontSize.value = _storage.getDouble(StorageKeys.fontSize) ?? 16.0;
  }
  
  Future<void> setFontSize(double size) async {
    await _storage.setDouble(StorageKeys.fontSize, size);
    fontSize.value = size;
  }
} 