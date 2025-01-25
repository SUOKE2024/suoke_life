import 'package:get/get.dart';
import 'package:flutter/material.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class LayoutService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final layouts = <String, Widget Function(BuildContext, Widget)>{}.obs;
  final layoutConfigs = <String, Map<String, dynamic>>{}.obs;
  final currentLayout = Rx<String?>(null);
  final layoutHistory = <Map<String, dynamic>>[].obs;

  @override
  void onInit() {
    super.onInit();
    _initLayouts();
  }

  Future<void> _initLayouts() async {
    try {
      await _loadLayoutConfigs();
      await _loadLayoutHistory();
      _registerDefaultLayouts();
      await _applyLastLayout();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize layouts', data: {'error': e.toString()});
    }
  }

  // 注册布局
  void registerLayout(
    String name,
    Widget Function(BuildContext, Widget) builder, [
    Map<String, dynamic>? config,
  ]) {
    try {
      layouts[name] = builder;
      if (config != null) {
        layoutConfigs[name] = config;
        _saveLayoutConfigs();
      }
    } catch (e) {
      _loggingService.log('error', 'Failed to register layout', data: {'name': name, 'error': e.toString()});
    }
  }

  // 应用布局
  Widget applyLayout(String name, BuildContext context, Widget child) {
    try {
      final builder = layouts[name];
      if (builder == null) {
        throw Exception('Layout not found: $name');
      }

      currentLayout.value = name;
      _recordLayoutChange(name);
      
      return builder(context, child);
    } catch (e) {
      _loggingService.log('error', 'Failed to apply layout', data: {'name': name, 'error': e.toString()});
      return child;
    }
  }

  // 更新布局配置
  Future<void> updateLayoutConfig(String name, Map<String, dynamic> config) async {
    try {
      if (!layouts.containsKey(name)) {
        throw Exception('Layout not found: $name');
      }

      layoutConfigs[name] = config;
      await _saveLayoutConfigs();
    } catch (e) {
      await _loggingService.log('error', 'Failed to update layout config', data: {'name': name, 'error': e.toString()});
      rethrow;
    }
  }

  // 获取布局配置
  Map<String, dynamic>? getLayoutConfig(String name) {
    try {
      return layoutConfigs[name];
    } catch (e) {
      _loggingService.log('error', 'Failed to get layout config', data: {'name': name, 'error': e.toString()});
      return null;
    }
  }

  // 获取布局历史
  Future<List<Map<String, dynamic>>> getLayoutHistory({
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      var history = layoutHistory.toList();

      if (startDate != null || endDate != null) {
        history = history.where((record) {
          final timestamp = DateTime.parse(record['timestamp']);
          if (startDate != null && timestamp.isBefore(startDate)) return false;
          if (endDate != null && timestamp.isAfter(endDate)) return false;
          return true;
        }).toList();
      }

      return history;
    } catch (e) {
      await _loggingService.log('error', 'Failed to get layout history', data: {'error': e.toString()});
      return [];
    }
  }

  void _registerDefaultLayouts() {
    // 注册默认布局
    registerLayout(
      'default',
      (context, child) => Scaffold(body: child),
      {'type': 'default', 'description': '默认布局'},
    );

    registerLayout(
      'with_drawer',
      (context, child) => Scaffold(
        drawer: const Drawer(),
        body: child,
      ),
      {'type': 'with_drawer', 'description': '带抽屉布局'},
    );

    registerLayout(
      'with_bottom_bar',
      (context, child) => Scaffold(
        body: child,
        bottomNavigationBar: BottomNavigationBar(items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: '首页'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: '我的'),
        ]),
      ),
      {'type': 'with_bottom_bar', 'description': '带底部导航栏布局'},
    );
  }

  Future<void> _loadLayoutConfigs() async {
    try {
      final configs = await _storageService.getLocal('layout_configs');
      if (configs != null) {
        layoutConfigs.value = Map<String, Map<String, dynamic>>.from(configs);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveLayoutConfigs() async {
    try {
      await _storageService.saveLocal('layout_configs', layoutConfigs.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadLayoutHistory() async {
    try {
      final history = await _storageService.getLocal('layout_history');
      if (history != null) {
        layoutHistory.value = List<Map<String, dynamic>>.from(history);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveLayoutHistory() async {
    try {
      await _storageService.saveLocal('layout_history', layoutHistory);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _applyLastLayout() async {
    try {
      final lastLayout = await _storageService.getLocal('last_layout');
      if (lastLayout != null) {
        currentLayout.value = lastLayout;
      } else {
        currentLayout.value = 'default';
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _recordLayoutChange(String name) async {
    try {
      final record = {
        'layout': name,
        'config': layoutConfigs[name],
        'timestamp': DateTime.now().toIso8601String(),
      };

      layoutHistory.insert(0, record);
      
      // 只保留最近100条记录
      if (layoutHistory.length > 100) {
        layoutHistory.removeRange(100, layoutHistory.length);
      }
      
      await _saveLayoutHistory();
      await _storageService.saveLocal('last_layout', name);
    } catch (e) {
      rethrow;
    }
  }
} 