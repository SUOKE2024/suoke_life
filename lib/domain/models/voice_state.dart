/// 语音状态枚举
enum VoiceState {
  /// 空闲状态
  idle,
  
  /// 正在监听
  listening,
  
  /// 正在处理
  processing,
  
  /// 正在播放
  speaking,
  
  /// 错误状态
  error,
} 