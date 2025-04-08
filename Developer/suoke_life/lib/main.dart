import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/app.dart';
import 'package:suoke_life/core/theme/app_theme.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:suoke_life/core/storage/preferences_manager.dart';
import 'package:suoke_life/core/utils/permission_utils.dart';
import 'package:suoke_life/domain/repositories/auth_repository.dart';
import 'package:suoke_life/core/config/env_config.dart';
import 'package:suoke_life/core/config/app_config.dart';
import 'package:suoke_life/core/utils/config.dart';
import 'package:suoke_life/di/providers/core_providers.dart';
import 'package:suoke_life/core/constants/api_constants.dart';
import 'package:dio/dio.dart';
import 'package:suoke_life/core/network/api_health_service.dart';
import 'package:suoke_life/core/utils/logger.dart';

/// 显式设置环境和启动应用
void main() async {
  // 确保Flutter绑定已初始化
  WidgetsFlutterBinding.ensureInitialized();
  
  // 配置自定义logger
  configureLogger();
  
  Logger.info('启动索克生活应用...');

  // 创建ProviderContainer
  final container = ProviderContainer();
  
  // 初始化核心providers
  await initializeCoreProviders(container);
  
  // 检查配置中是否有指定的运行环境
  final configService = container.read(configServiceProvider);
  final env = await configService.getEnvironment();
  if (env != null && env.isNotEmpty) {
    Logger.info('正在设置API环境为: $env');
    ApiConstants.setEnvironment(env);
  }
  
  // 进行API健康检查
  try {
    Logger.info('正在检查API健康状态...');
    final apiHealthService = container.read(apiHealthServiceProvider);
    final isHealthy = await apiHealthService.checkAllServices();
    
    if (isHealthy) {
      Logger.info('API服务健康状态良好');
    } else {
      Logger.warning('API服务健康状态异常');
      // 尝试自动切换环境
      _tryAlternativeEnvironment(container);
    }
  } catch (e) {
    Logger.error('API健康检查失败: $e');
    // 尝试自动切换环境
    _tryAlternativeEnvironment(container);
  }
  
  // 运行应用
  runApp(
    UncontrolledProviderScope(
      container: container,
      child: const SuokeApp(),
    ),
  );
}

/// 尝试切换到备用环境
void _tryAlternativeEnvironment(ProviderContainer container) async {
  // 如果当前是生产环境，尝试切换到测试环境
  if (ApiConstants.environment == 'prod') {
    Logger.info('尝试切换到测试环境...');
    ApiConstants.setEnvironment('test');
    
    // 保存环境设置
    final configService = container.read(configServiceProvider);
    await configService.setEnvironment('test');
    
    // 重新检查API健康状态
    final apiHealthService = container.read(apiHealthServiceProvider);
    try {
      final isHealthy = await apiHealthService.checkAllServices();
      if (isHealthy) {
        Logger.info('测试环境API服务健康状态良好');
      } else {
        Logger.warning('测试环境API服务健康状态也异常');
        // 如果测试环境也不可用，切换回生产环境
        ApiConstants.setEnvironment('prod');
        await configService.setEnvironment('prod');
      }
    } catch (e) {
      Logger.error('测试环境API健康检查失败: $e');
      // 如果检查失败，切换回生产环境
      ApiConstants.setEnvironment('prod');
      await configService.setEnvironment('prod');
    }
  }
}

/// 初始化应用所需的环境和配置
Future<Map<String, dynamic>> initializeApp() async {
  print('开始初始化应用...');

  // 初始化环境配置
  await EnvConfig().initialize();
  print('环境配置已初始化');

  // 初始化偏好设置管理器
  final preferencesManager = await initPreferencesManager();

  // 初始化应用配置
  final appConfigNotifier = AppConfigNotifier();
  // 等待配置加载完成
  await Future.delayed(const Duration(milliseconds: 100));
  print('应用配置已初始化: ${appConfigNotifier.debugState.themeMode}');

  // 重置欢迎页面显示状态，确保每次启动都显示欢迎页面
  await preferencesManager.setHasSeenWelcome(false);
  print('已重置欢迎页面状态: hasSeenWelcome = ${preferencesManager.hasSeenWelcome}');

  try {
    // 请求必要的权限
    await PermissionUtils.requestAllPermissions();
  } catch (e) {
    debugPrint('请求权限时发生错误: $e');
    // 继续执行，不中断初始化流程
  }

  // 强制登出用户，确保每次启动都需要重新登录
  final authRepository = MockAuthRepository();
  await authRepository.logout();
  print('已强制登出用户: isAuthenticated = ${authRepository.isAuthenticated}');

  // TODO: 初始化数据库
  // TODO: 初始化网络客户端
  // TODO: 初始化本地存储
  // TODO: 初始化AI代理
  // TODO: 加载用户配置
  // 可以在这里添加更多初始化逻辑

  return {
    'preferencesManager': preferencesManager,
    'appConfigNotifier': appConfigNotifier,
  };
}
