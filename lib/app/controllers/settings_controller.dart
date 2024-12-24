import 'package:flutter/material.dart';
import 'package:get/get.dart';

class SettingsController extends GetxController {
  final themeMode = ThemeMode.system.obs;
  final fontSize = 16.0.obs;

  void setThemeMode(ThemeMode mode) {
    themeMode.value = mode;
    Get.changeThemeMode(mode);
  }

  void setFontSize(double size) {
    fontSize.value = size;
  }
} 