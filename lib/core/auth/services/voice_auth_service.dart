import 'dart:async';
import 'dart:io';
import 'package:get/get.dart';

import 'package:record/record.dart';
import '../../storage/services/secure_storage_service.dart';
import '../../network/dio_client.dart';
import 'auth_service.dart';

class VoiceAuthService extends GetxService {
  static VoiceAuthService get to => Get.find();
  
  final _record = Record();
  final _storage = Get.find<SecureStorageService>();
  final _dioClient = Get.find<DioClient>();
  final _authService = Get.find<AuthService>();
  
  final _isVoiceEnabled = false.obs;
  final _isRecording = false.obs;
  final _recordDuration = 0.obs;
  
  bool get isVoiceEnabled => _isVoiceEnabled.value;
  bool get isRecording => _isRecording.value;
  int get recordDuration => _recordDuration.value;
  
  Timer? _recordTimer;
  String? _tempRecordPath;
  
  // 初始化服务
  Future<VoiceAuthService> init() async {
    final enabled = await _storage.read('voice_auth_enabled');
    _isVoiceEnabled.value = enabled == 'true';
    return this;
  }
  
  // 检查麦克风权限
  Future<bool> checkMicrophonePermission() async {
    return await _record.hasPermission();
  }
  
  // 开始录音
  Future<bool> startRecording() async {
    if (isRecording) return false;
    
    try {
      final hasPermission = await checkMicrophonePermission();
      if (!hasPermission) {
        throw Exception('没有麦克风权限');
      }
      
      // 获取临时文件路径
      final tempDir = await getTemporaryDirectory();
      _tempRecordPath = '${tempDir.path}/voice_auth_${DateTime.now().millisecondsSinceEpoch}.wav';
      
      // 开始录音
      await _record.start(
        path: _tempRecordPath,
        encoder: AudioEncoder.wav,
        bitRate: 16000,
        samplingRate: 16000,
      );
      
      _isRecording.value = true;
      _recordDuration.value = 0;
      
      // 开始计时
      _recordTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
        _recordDuration.value++;
        // 限制录音时长为5秒
        if (_recordDuration.value >= 5) {
          stopRecording();
        }
      });
      
      return true;
    } catch (e) {
      Get.snackbar('错误', '开始录音失败：${e.toString()}');
      return false;
    }
  }
  
  // 停止录音
  Future<String?> stopRecording() async {
    if (!isRecording) return null;
    
    try {
      _recordTimer?.cancel();
      await _record.stop();
      _isRecording.value = false;
      return _tempRecordPath;
    } catch (e) {
      Get.snackbar('错误', '停止录音失败：${e.toString()}');
      return null;
    }
  }
  
  // 注册声纹
  Future<bool> enrollVoicePrint() async {
    try {
      final recordPath = await stopRecording();
      if (recordPath == null) return false;
      
      // 上传声纹数据
      final formData = FormData.fromMap({
        'voice_file': await MultipartFile.fromFile(recordPath),
      });
      
      final response = await _dioClient.post(
        '/auth/voice/enroll',
        data: formData,
      );
      
      if (response.data['success'] == true) {
        // 保存声纹ID
        final voicePrintId = response.data['voice_print_id'];
        await _storage.write('voice_print_id', voicePrintId);
        await _storage.write('voice_auth_enabled', 'true');
        _isVoiceEnabled.value = true;
        return true;
      }
      return false;
    } catch (e) {
      Get.snackbar('错误', '注册声纹失败：${e.toString()}');
      return false;
    } finally {
      // 清理临时文件
      if (_tempRecordPath != null) {
        try {
          await File(_tempRecordPath!).delete();
        } catch (_) {}
      }
    }
  }
  
  // 声纹验证
  Future<bool> verifyVoicePrint() async {
    try {
      final recordPath = await stopRecording();
      if (recordPath == null) return false;
      
      // 获取声纹ID
      final voicePrintId = await _storage.read('voice_print_id');
      if (voicePrintId == null) return false;
      
      // 上传声纹数据进行验证
      final formData = FormData.fromMap({
        'voice_file': await MultipartFile.fromFile(recordPath),
        'voice_print_id': voicePrintId,
      });
      
      final response = await _dioClient.post(
        '/auth/voice/verify',
        data: formData,
      );
      
      if (response.data['success'] == true) {
        // 验证成功，使用返回的token登录
        final token = response.data['token'];
        if (token != null) {
          await _authService._handleLoginSuccess(token);
          return true;
        }
      }
      return false;
    } catch (e) {
      Get.snackbar('错误', '声纹验证失败：${e.toString()}');
      return false;
    } finally {
      // 清理临时文件
      if (_tempRecordPath != null) {
        try {
          await File(_tempRecordPath!).delete();
        } catch (_) {}
      }
    }
  }
  
  // 禁用声纹认证
  Future<void> disableVoiceAuth() async {
    try {
      await _dioClient.post('/auth/voice/disable');
      await _storage.delete('voice_print_id');
      await _storage.write('voice_auth_enabled', 'false');
      _isVoiceEnabled.value = false;
    } catch (e) {
      Get.snackbar('错误', '禁用声纹认证失败：${e.toString()}');
    }
  }
  
  @override
  void onClose() {
    _recordTimer?.cancel();
    _record.dispose();
    super.onClose();
  }
} 