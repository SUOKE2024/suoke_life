import 'package:get/get.dart';
import '../../services/settings_service.dart';
import './base_settings_controller.dart';

class VoiceSettingsController extends BaseSettingsController {
  final SettingsService _settingsService = Get.find();
  
  // 语音识别开关
  final isRecognitionEnabled = false.obs;
  // 语音合成开关
  final isSynthesisEnabled = false.obs;
  // 音量控制
  final volume = 0.7.obs;
  // 语速控制
  final speed = 1.0.obs;

  @override
  Future<void> loadSettings() async {
    try {
      final settings = _settingsService.getVoiceSettings();
      isRecognitionEnabled.value = settings['recognition'] ?? false;
      isSynthesisEnabled.value = settings['synthesis'] ?? false;
      volume.value = settings['volume'] ?? 0.7;
      speed.value = settings['speed'] ?? 1.0;
    } catch (e) {
      print('Error loading voice settings: $e');
    }
  }

  @override
  Future<void> saveSettings() async {
    try {
      await _settingsService.setVoiceSettings({
        'recognition': isRecognitionEnabled.value,
        'synthesis': isSynthesisEnabled.value,
        'volume': volume.value,
        'speed': speed.value,
      });
      Get.snackbar('成功', '语音设置已保存');
    } catch (e) {
      print('Error saving voice settings: $e');
      Get.snackbar('错误', '保存语音设置失败');
    }
  }

  // 更新语音识别状态
  void toggleRecognition(bool enabled) {
    isRecognitionEnabled.value = enabled;
    saveSettings();
  }

  // 更新语音合成状态
  void toggleSynthesis(bool enabled) {
    isSynthesisEnabled.value = enabled;
    saveSettings();
  }

  // 更新音量
  void updateVolume(double value) {
    volume.value = value;
    saveSettings();
  }

  // 更新语速
  void updateSpeed(double value) {
    speed.value = value;
    saveSettings();
  }

  // 重置所有设置
  void resetSettings() {
    isRecognitionEnabled.value = false;
    isSynthesisEnabled.value = false;
    volume.value = 0.7;
    speed.value = 1.0;
    saveSettings();
  }
} 