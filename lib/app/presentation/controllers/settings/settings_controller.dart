import 'package:get/get.dart';
import '../../../services/settings_service.dart';

class SettingsController extends GetxController {
  final SettingsService _settingsService = Get.find();
  
  final Rx<String> _currentLanguage = 'zh_CN'.obs;
  final Rx<String> _currentTheme = 'system'.obs;
  
  String get currentLanguage => _currentLanguage.value;
  String get currentTheme => _currentTheme.value;
  
  @override
  void onInit() {
    super.onInit();
    _loadSettings();
  }
  
  void _loadSettings() {
    _currentLanguage.value = _settingsService.getSetting('general.language', defaultValue: 'zh_CN') ?? 'zh_CN';
    _currentTheme.value = _settingsService.getSetting('general.theme', defaultValue: 'system') ?? 'system';
  }
  
  Future<void> updateLanguage(String language) async {
    await _settingsService.updateSetting('general.language', language);
    _currentLanguage.value = language;
  }
  
  Future<void> updateTheme(String theme) async {
    await _settingsService.updateSetting('general.theme', theme);
    _currentTheme.value = theme;
  }
} 