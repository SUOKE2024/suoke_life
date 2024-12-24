import 'package:get/get.dart';

abstract class BaseSettingsController extends GetxController {
  @override
  void onInit() {
    super.onInit();
    loadSettings();
  }

  Future<void> loadSettings();
  Future<void> saveSettings();
} 