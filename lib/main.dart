import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/ai_agents/llm_manager.dart';
import 'package:suoke_life/app.dart';
import 'package:suoke_life/di/providers.dart';

void main() async {
  // 确保Flutter初始化完毕
  WidgetsFlutterBinding.ensureInitialized();
  
  debugPrint('索克生活启动 - Flutter引擎初始化完成');
  
  // 加载环境变量
  try {
    await dotenv.load(fileName: 'assets/config/.env');
    debugPrint('索克生活启动 - 环境变量加载完成');
  } catch (e) {
    debugPrint('索克生活启动 - 环境变量加载失败: $e');
    debugPrint('索克生活启动 - 使用默认环境变量');
    // 手动设置一些基本环境变量 (临时硬编码用于调试)
    dotenv.env['DEEPSEEK_API_KEY'] = 'mock_api_key_for_development';
    // 添加其他可能的关键环境变量
    dotenv.env['API_BASE_URL'] = 'http://localhost:3000'; // 示例
    dotenv.env['ANOTHER_SERVICE_KEY'] = 'mock_service_key'; // 示例
  }
  
  // 初始化SharedPreferences
  final sharedPreferences = await SharedPreferences.getInstance();
  debugPrint('索克生活启动 - SharedPreferences初始化完成');
  
  // 初始化LLM管理器
  final llmManager = LLMManager();
  await llmManager.initialize();
  debugPrint('索克生活启动 - LLM管理器初始化完成');
  
  // 启动应用
  debugPrint('索克生活启动 - 准备运行应用');
  runApp(
    ProviderScope(
      overrides: [
        // 覆盖SharedPreferences提供者
        sharedPreferencesProvider.overrideWithValue(sharedPreferences),
      ],
      child: const SuokeLifeApp(),
    ),
  );
  debugPrint('索克生活启动 - 应用构建完成');
}