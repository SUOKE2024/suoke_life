import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../logging/app_logger.dart';
import 'route_analytics.dart';

class RouteErrorHandler {
  static final RouteErrorHandler _instance = RouteErrorHandler._internal();
  static RouteErrorHandler get instance => _instance;
  
  RouteErrorHandler._internal();
  
  // 处理路由错误
  Route<dynamic>? onGenerateRoute(RouteSettings settings) {
    try {
      // 记录未找到的路由
      AppLogger.instance.warning(
        'Route not found: ${settings.name}',
        tags: ['ROUTE', 'ERROR'],
      );
      
      // 返回错误页面
      return MaterialPageRoute(
        settings: settings,
        builder: (context) => _buildErrorPage(settings),
      );
    } catch (e, s) {
      // 记录错误
      AppLogger.instance.error(
        'Route generation error',
        error: e,
        stackTrace: s,
        tags: ['ROUTE', 'ERROR'],
      );
      
      // 返回通用错误页面
      return MaterialPageRoute(
        settings: settings,
        builder: (context) => _buildGeneralErrorPage(e),
      );
    }
  }
  
  // 处理路由重定向
  Route<dynamic>? onUnknownRoute(RouteSettings settings) {
    // 记录重定向
    AppLogger.instance.info(
      'Route redirected: ${settings.name}',
      tags: ['ROUTE', 'REDIRECT'],
    );
    
    // 返回404页面
    return MaterialPageRoute(
      settings: settings,
      builder: (context) => _build404Page(settings),
    );
  }
  
  // 构建路由错误页面
  Widget _buildErrorPage(RouteSettings settings) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('页面错误'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Get.back(),
        ),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.orange,
            ),
            const SizedBox(height: 16),
            Text(
              '无法找到页面: ${settings.name}',
              style: Get.textTheme.titleLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              '请检查页面路径是否正确',
              style: Get.textTheme.bodyMedium,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => Get.back(),
              child: const Text('返回上一页'),
            ),
          ],
        ),
      ),
    );
  }
  
  // 构建通用错误页面
  Widget _buildGeneralErrorPage(Object error) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('系统错误'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Get.back(),
        ),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.warning_amber_rounded,
              size: 64,
              color: Colors.red,
            ),
            const SizedBox(height: 16),
            const Text(
              '系统发生错误',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32),
              child: Text(
                error.toString(),
                style: const TextStyle(color: Colors.grey),
                textAlign: TextAlign.center,
              ),
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton(
                  onPressed: () => Get.back(),
                  child: const Text('返回'),
                ),
                const SizedBox(width: 16),
                ElevatedButton(
                  onPressed: () {
                    // 重试当前路由
                    final currentRoute = Get.currentRoute;
                    Get.offNamed(currentRoute);
                  },
                  child: const Text('重试'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  // 构建404页面
  Widget _build404Page(RouteSettings settings) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('页面不存在'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Get.back(),
        ),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.search_off_rounded,
              size: 64,
              color: Colors.grey,
            ),
            const SizedBox(height: 16),
            const Text(
              '404',
              style: TextStyle(
                fontSize: 48,
                fontWeight: FontWeight.bold,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '找不到页面: ${settings.name}',
              style: const TextStyle(color: Colors.grey),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => Get.back(),
              child: const Text('返回首页'),
            ),
          ],
        ),
      ),
    );
  }
  
  // 处理路由异常
  void handleRouteException(Object error, StackTrace stackTrace) {
    // 记录错误
    AppLogger.instance.error(
      'Route exception',
      error: error,
      stackTrace: stackTrace,
      tags: ['ROUTE', 'ERROR'],
    );
    
    // 显示错误提示
    Get.snackbar(
      '路由错误',
      error.toString(),
      snackPosition: SnackPosition.BOTTOM,
      backgroundColor: Colors.red,
      colorText: Colors.white,
      duration: const Duration(seconds: 3),
    );
  }
} 