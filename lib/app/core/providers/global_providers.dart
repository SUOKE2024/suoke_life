import 'package:flutter_riverpod/flutter_riverpod.dart';

// 全局配置
final configProvider = StateNotifierProvider<ConfigNotifier, AppConfig>((ref) {
  return ConfigNotifier();
});

// 用户会话
final sessionProvider = StateNotifierProvider<SessionNotifier, UserSession>((ref) {
  return SessionNotifier();
});

// AI助手状态
final aiAssistantProvider = StateNotifierProvider<AIAssistantNotifier, AIAssistantState>((ref) {
  return AIAssistantNotifier();
});

// 主题模式
final themeModeProvider = StateProvider<ThemeMode>((ref) {
  return ThemeMode.system;
}); 