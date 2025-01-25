import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';
import 'file_manager_service.dart';

class ResourceManagerService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final FileManagerService _fileManager = Get.find();

  final resources = <String, dynamic>{}.obs;
  final resourceUsage = <String, int>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _initResourceManager();
  }

  Future<void> _initResourceManager() async {
    try {
      await _loadResourceConfig();
      await _loadResources();
      await _checkResourceUsage();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize resource manager', data: {'error': e.toString()});
    }
  }

  // 加载资源
  Future<dynamic> loadResource(String key) async {
    try {
      if (resources.containsKey(key)) {
        return resources[key];
      }

      final resource = await _loadResourceFromStorage(key);
      if (resource != null) {
        resources[key] = resource;
        await _updateResourceUsage(key);
      }
      return resource;
    } catch (e) {
      await _loggingService.log('error', 'Failed to load resource', data: {'key': key, 'error': e.toString()});
      return null;
    }
  }

  // 保存资源
  Future<void> saveResource(String key, dynamic data) async {
    try {
      await _storageService.saveLocal('resource_$key', {
        'data': data,
        'timestamp': DateTime.now().toIso8601String(),
      });
      
      resources[key] = data;
      await _updateResourceUsage(key);
    } catch (e) {
      await _loggingService.log('error', 'Failed to save resource', data: {'key': key, 'error': e.toString()});
      rethrow;
    }
  }

  // 释放资源
  Future<void> releaseResource(String key) async {
    try {
      resources.remove(key);
      resourceUsage.remove(key);
    } catch (e) {
      await _loggingService.log('error', 'Failed to release resource', data: {'key': key, 'error': e.toString()});
      rethrow;
    }
  }

  // 清理资源
  Future<void> clearResources() async {
    try {
      resources.clear();
      resourceUsage.clear();
      await _storageService.removeLocal('resource_usage');
    } catch (e) {
      await _loggingService.log('error', 'Failed to clear resources', data: {'error': e.toString()});
      rethrow;
    }
  }

  Future<void> _loadResourceConfig() async {
    try {
      final config = await _storageService.getLocal('resource_config');
      if (config == null) {
        await _saveDefaultConfig();
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveDefaultConfig() async {
    try {
      await _storageService.saveLocal('resource_config', {
        'max_memory_usage': 256 * 1024 * 1024, // 256MB
        'auto_release': true,
        'preload_resources': ['common_assets', 'user_preferences'],
      });
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadResources() async {
    try {
      final config = await _storageService.getLocal('resource_config');
      if (config != null && config['preload_resources'] != null) {
        for (final key in config['preload_resources']) {
          await loadResource(key);
        }
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<dynamic> _loadResourceFromStorage(String key) async {
    try {
      final data = await _storageService.getLocal('resource_$key');
      return data?['data'];
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _updateResourceUsage(String key) async {
    try {
      final size = _calculateResourceSize(resources[key]);
      resourceUsage[key] = size;
      
      await _storageService.saveLocal('resource_usage', resourceUsage);
      await _checkResourceUsage();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _checkResourceUsage() async {
    try {
      final config = await _storageService.getLocal('resource_config');
      if (config == null) return;

      final maxUsage = config['max_memory_usage'] ?? (256 * 1024 * 1024);
      final totalUsage = resourceUsage.values.fold<int>(0, (sum, size) => sum + size);

      if (totalUsage > maxUsage && config['auto_release'] == true) {
        await _releaseUnusedResources();
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _releaseUnusedResources() async {
    try {
      final unusedResources = resources.keys.where((key) {
        // TODO: 实现资源使用情况检测
        return false;
      }).toList();

      for (final key in unusedResources) {
        await releaseResource(key);
      }
    } catch (e) {
      rethrow;
    }
  }

  int _calculateResourceSize(dynamic resource) {
    // TODO: 实现资源大小计算
    return 0;
  }
} 