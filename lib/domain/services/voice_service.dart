import 'package:suoke_life/domain/models/voice_state.dart';

/// 语音服务接口
abstract class VoiceService {
  /// 初始化语音服务
  Future<void> initialize();
  
  /// 开始语音识别
  Future<void> startListening();
  
  /// 停止语音识别
  Future<void> stopListening();
  
  /// 获取当前识别结果
  Future<String> getRecognitionResult();
  
  /// 播放文本为语音
  Future<void> speak(String text);
  
  /// 停止语音播放
  Future<void> stopSpeaking();
  
  /// 获取当前语音状态
  Future<VoiceState> getState();
  
  /// 处置资源
  Future<void> dispose();
} 