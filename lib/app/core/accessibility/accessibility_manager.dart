import 'package:get/get.dart';
import '../storage/storage_service.dart';

class AccessibilityManager {
  final _config = <String, dynamic>{}.obs;
  
  Future<void> initialize() async {
    // 加载无障碍配置
    _config.value = await Get.find<StorageService>().get('accessibility_config');
    
    // 设置默认值
    _config['screen_reader_enabled'] ??= false;
    _config['high_contrast'] ??= false;
    _config['font_scale'] ??= 1.0;
  }

  bool get isScreenReaderEnabled => _config['screen_reader_enabled'];
  bool get isHighContrastEnabled => _config['high_contrast'];
  double get fontScale => _config['font_scale'];

  Future<void> toggleScreenReader(bool value) async {
    _config['screen_reader_enabled'] = value;
    await _saveConfig();
  }

  Future<void> toggleHighContrast(bool value) async {
    _config['high_contrast'] = value;
    await _saveConfig();
  }

  Future<void> setFontScale(double scale) async {
    _config['font_scale'] = scale;
    await _saveConfig();
  }

  Future<void> _saveConfig() async {
    await Get.find<StorageService>().set('accessibility_config', _config);
  }
} 