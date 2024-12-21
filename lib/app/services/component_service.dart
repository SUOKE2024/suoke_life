import 'package:get/get.dart';
import 'package:flutter/material.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class ComponentService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final components = <String, Widget Function(BuildContext)>{}.obs;
  final componentConfigs = <String, Map<String, dynamic>>{}.obs;
  final componentHistory = <Map<String, dynamic>>[].obs;

  @override
  void onInit() {
    super.onInit();
    _initComponents();
  }

  Future<void> _initComponents() async {
    try {
      await _loadComponentConfigs();
      await _loadComponentHistory();
      _registerDefaultComponents();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize components', data: {'error': e.toString()});
    }
  }

  // 注册组件
  void registerComponent(
    String name,
    Widget Function(BuildContext) builder, [
    Map<String, dynamic>? config,
  ]) {
    try {
      components[name] = builder;
      if (config != null) {
        componentConfigs[name] = config;
        _saveComponentConfigs();
      }
    } catch (e) {
      _loggingService.log('error', 'Failed to register component', data: {'name': name, 'error': e.toString()});
    }
  }

  // 获取组件
  Widget? getComponent(String name, BuildContext context) {
    try {
      final builder = components[name];
      if (builder != null) {
        _recordComponentUsage(name);
        return builder(context);
      }
      return null;
    } catch (e) {
      _loggingService.log('error', 'Failed to get component', data: {'name': name, 'error': e.toString()});
      return null;
    }
  }

  // 更新组件配置
  Future<void> updateComponentConfig(String name, Map<String, dynamic> config) async {
    try {
      if (!components.containsKey(name)) {
        throw Exception('Component not found: $name');
      }

      componentConfigs[name] = config;
      await _saveComponentConfigs();
    } catch (e) {
      await _loggingService.log('error', 'Failed to update component config', data: {'name': name, 'error': e.toString()});
      rethrow;
    }
  }

  // 获取组件配置
  Map<String, dynamic>? getComponentConfig(String name) {
    try {
      return componentConfigs[name];
    } catch (e) {
      _loggingService.log('error', 'Failed to get component config', data: {'name': name, 'error': e.toString()});
      return null;
    }
  }

  // 获取组件使用历史
  Future<List<Map<String, dynamic>>> getComponentHistory({
    String? name,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      var history = componentHistory.toList();

      if (name != null) {
        history = history.where((record) => record['name'] == name).toList();
      }

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
      await _loggingService.log('error', 'Failed to get component history', data: {'error': e.toString()});
      return [];
    }
  }

  void _registerDefaultComponents() {
    // 注册默认组件
    registerComponent(
      'loading',
      (context) => const Center(child: CircularProgressIndicator()),
      {'type': 'loading', 'description': '加载指示器'},
    );

    registerComponent(
      'error',
      (context) => const Center(child: Icon(Icons.error)),
      {'type': 'error', 'description': '错误提示'},
    );

    registerComponent(
      'empty',
      (context) => const Center(child: Text('暂无数据')),
      {'type': 'empty', 'description': '空数据提示'},
    );
  }

  Future<void> _loadComponentConfigs() async {
    try {
      final configs = await _storageService.getLocal('component_configs');
      if (configs != null) {
        componentConfigs.value = Map<String, Map<String, dynamic>>.from(configs);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveComponentConfigs() async {
    try {
      await _storageService.saveLocal('component_configs', componentConfigs.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadComponentHistory() async {
    try {
      final history = await _storageService.getLocal('component_history');
      if (history != null) {
        componentHistory.value = List<Map<String, dynamic>>.from(history);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveComponentHistory() async {
    try {
      await _storageService.saveLocal('component_history', componentHistory);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _recordComponentUsage(String name) async {
    try {
      final record = {
        'name': name,
        'config': componentConfigs[name],
        'timestamp': DateTime.now().toIso8601String(),
      };

      componentHistory.insert(0, record);
      
      // 只保留最近1000条记录
      if (componentHistory.length > 1000) {
        componentHistory.removeRange(1000, componentHistory.length);
      }
      
      await _saveComponentHistory();
    } catch (e) {
      rethrow;
    }
  }
} 