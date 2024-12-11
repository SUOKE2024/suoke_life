import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../logging/app_logger.dart';
import 'route_analytics.dart';

mixin RouteLifecycleMixin<T extends StatefulWidget> on State<T> {
  bool _isFirstBuild = true;
  DateTime? _pageStartTime;
  
  @override
  void initState() {
    super.initState();
    _pageStartTime = DateTime.now();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      onPageStart();
    });
  }
  
  @override
  void dispose() {
    onPageEnd();
    super.dispose();
  }
  
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_isFirstBuild) {
      onPageFirstBuild();
      _isFirstBuild = false;
    }
  }
  
  // 页面首次构建完成时调用
  void onPageFirstBuild() {
    final routeName = ModalRoute.of(context)?.settings.name;
    if (routeName != null) {
      AppLogger.instance.info(
        'Page First Build: $routeName',
        tags: ['LIFECYCLE'],
      );
    }
  }
  
  // 页面开始时调用
  void onPageStart() {
    final routeName = ModalRoute.of(context)?.settings.name;
    if (routeName != null) {
      AppLogger.instance.info(
        'Page Start: $routeName',
        tags: ['LIFECYCLE'],
      );
    }
  }
  
  // 页面结束时调用
  void onPageEnd() {
    final routeName = ModalRoute.of(context)?.settings.name;
    if (routeName != null && _pageStartTime != null) {
      final duration = DateTime.now().difference(_pageStartTime!);
      RouteAnalytics.to.recordPageDuration(routeName, duration);
      AppLogger.instance.info(
        'Page End: $routeName, Duration: ${duration.inSeconds}s',
        tags: ['LIFECYCLE'],
      );
    }
  }
  
  // 页面获得焦点时调用
  void onPageResume() {
    final routeName = ModalRoute.of(context)?.settings.name;
    if (routeName != null) {
      AppLogger.instance.info(
        'Page Resume: $routeName',
        tags: ['LIFECYCLE'],
      );
    }
  }
  
  // 页面失去焦点时调用
  void onPagePause() {
    final routeName = ModalRoute.of(context)?.settings.name;
    if (routeName != null) {
      AppLogger.instance.info(
        'Page Pause: $routeName',
        tags: ['LIFECYCLE'],
      );
    }
  }
  
  // 页面可见性变化时调用
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);
    final routeName = ModalRoute.of(context)?.settings.name;
    if (routeName != null) {
      switch (state) {
        case AppLifecycleState.resumed:
          onPageResume();
          break;
        case AppLifecycleState.paused:
          onPagePause();
          break;
        default:
          break;
      }
    }
  }
}

// 基础页面类，集成了生命周期管理
abstract class BasePageState<T extends StatefulWidget> extends State<T>
    with RouteLifecycleMixin<T>, WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }
  
  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }
  
  // 页面构建前的准备工作
  Future<void> onPagePreBuild() async {}
  
  // 页面重新构建时的处理
  void onPageRebuild() {}
  
  // 页面出错时的处理
  void onPageError(Object error, StackTrace stackTrace) {
    AppLogger.instance.error(
      'Page Error: ${error.toString()}',
      error: error,
      stackTrace: stackTrace,
      tags: ['LIFECYCLE', 'ERROR'],
    );
  }
  
  @override
  Widget build(BuildContext context) {
    try {
      onPageRebuild();
      return buildPage(context);
    } catch (e, s) {
      onPageError(e, s);
      return _buildErrorWidget(e);
    }
  }
  
  // 构建实际的页面内容
  Widget buildPage(BuildContext context);
  
  // 构建错误提示页面
  Widget _buildErrorWidget(Object error) {
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
              color: Colors.red,
            ),
            const SizedBox(height: 16),
            Text(
              '页面加载出错',
              style: Get.textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              error.toString(),
              style: Get.textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                setState(() {});
              },
              child: const Text('重试'),
            ),
          ],
        ),
      ),
    );
  }
} 