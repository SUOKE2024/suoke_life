import 'package:get/get.dart';
import 'package:flutter/material.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class StyleService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final styles = <String, dynamic>{}.obs;
  final currentStyle = ''.obs;
  final customStyles = <String, Map<String, dynamic>>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _initStyles();
  }

  Future<void> _initStyles() async {
    try {
      await _loadStyles();
      await _loadCustomStyles();
      await _applyCurrentStyle();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize styles', data: {'error': e.toString()});
    }
  }

  // 更新样式
  Future<void> updateStyle(String styleName) async {
    try {
      if (!styles.containsKey(styleName)) {
        throw Exception('Style not found: $styleName');
      }

      currentStyle.value = styleName;
      await _applyCurrentStyle();
      await _saveStyleSettings();
    } catch (e) {
      await _loggingService.log('error', 'Failed to update style', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 添加自定义样式
  Future<void> addCustomStyle(String name, Map<String, dynamic> style) async {
    try {
      customStyles[name] = style;
      await _saveCustomStyles();
    } catch (e) {
      await _loggingService.log('error', 'Failed to add custom style', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 删除自定义样式
  Future<void> removeCustomStyle(String name) async {
    try {
      customStyles.remove(name);
      await _saveCustomStyles();
    } catch (e) {
      await _loggingService.log('error', 'Failed to remove custom style', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 获取样式
  Map<String, dynamic>? getStyle(String name) {
    try {
      return customStyles[name] ?? styles[name];
    } catch (e) {
      _loggingService.log('error', 'Failed to get style', data: {'name': name, 'error': e.toString()});
      return null;
    }
  }

  Future<void> _loadStyles() async {
    try {
      // 加载预定义样式
      styles.value = {
        'default': _getDefaultStyle(),
        'modern': _getModernStyle(),
        'classic': _getClassicStyle(),
        'minimal': _getMinimalStyle(),
      };

      // 加载当前样式设置
      final settings = await _storageService.getLocal('style_settings');
      if (settings != null) {
        currentStyle.value = settings['current_style'] ?? 'default';
      } else {
        currentStyle.value = 'default';
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadCustomStyles() async {
    try {
      final saved = await _storageService.getLocal('custom_styles');
      if (saved != null) {
        customStyles.value = Map<String, Map<String, dynamic>>.from(saved);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveStyleSettings() async {
    try {
      await _storageService.saveLocal('style_settings', {
        'current_style': currentStyle.value,
        'updated_at': DateTime.now().toIso8601String(),
      });
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveCustomStyles() async {
    try {
      await _storageService.saveLocal('custom_styles', customStyles);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _applyCurrentStyle() async {
    try {
      final style = getStyle(currentStyle.value);
      if (style != null) {
        // TODO: 应用样式到应用
      }
    } catch (e) {
      rethrow;
    }
  }

  Map<String, dynamic> _getDefaultStyle() {
    return {
      'spacing': {
        'small': 8.0,
        'medium': 16.0,
        'large': 24.0,
      },
      'radius': {
        'small': 4.0,
        'medium': 8.0,
        'large': 12.0,
      },
      'elevation': {
        'none': 0.0,
        'low': 2.0,
        'medium': 4.0,
        'high': 8.0,
      },
      'typography': {
        'h1': {'size': 24.0, 'weight': FontWeight.bold},
        'h2': {'size': 20.0, 'weight': FontWeight.bold},
        'h3': {'size': 18.0, 'weight': FontWeight.bold},
        'body': {'size': 16.0, 'weight': FontWeight.normal},
        'caption': {'size': 14.0, 'weight': FontWeight.normal},
      },
    };
  }

  Map<String, dynamic> _getModernStyle() {
    return {
      'spacing': {
        'small': 12.0,
        'medium': 20.0,
        'large': 32.0,
      },
      'radius': {
        'small': 8.0,
        'medium': 16.0,
        'large': 24.0,
      },
      'elevation': {
        'none': 0.0,
        'low': 4.0,
        'medium': 8.0,
        'high': 16.0,
      },
      'typography': {
        'h1': {'size': 28.0, 'weight': FontWeight.w900},
        'h2': {'size': 24.0, 'weight': FontWeight.w700},
        'h3': {'size': 20.0, 'weight': FontWeight.w600},
        'body': {'size': 16.0, 'weight': FontWeight.normal},
        'caption': {'size': 14.0, 'weight': FontWeight.w300},
      },
    };
  }

  Map<String, dynamic> _getClassicStyle() {
    return {
      'spacing': {
        'small': 6.0,
        'medium': 12.0,
        'large': 18.0,
      },
      'radius': {
        'small': 2.0,
        'medium': 4.0,
        'large': 6.0,
      },
      'elevation': {
        'none': 0.0,
        'low': 1.0,
        'medium': 2.0,
        'high': 4.0,
      },
      'typography': {
        'h1': {'size': 22.0, 'weight': FontWeight.w600},
        'h2': {'size': 18.0, 'weight': FontWeight.w600},
        'h3': {'size': 16.0, 'weight': FontWeight.w600},
        'body': {'size': 14.0, 'weight': FontWeight.normal},
        'caption': {'size': 12.0, 'weight': FontWeight.normal},
      },
    };
  }

  Map<String, dynamic> _getMinimalStyle() {
    return {
      'spacing': {
        'small': 4.0,
        'medium': 8.0,
        'large': 16.0,
      },
      'radius': {
        'small': 0.0,
        'medium': 2.0,
        'large': 4.0,
      },
      'elevation': {
        'none': 0.0,
        'low': 1.0,
        'medium': 2.0,
        'high': 3.0,
      },
      'typography': {
        'h1': {'size': 20.0, 'weight': FontWeight.w500},
        'h2': {'size': 18.0, 'weight': FontWeight.w500},
        'h3': {'size': 16.0, 'weight': FontWeight.w500},
        'body': {'size': 14.0, 'weight': FontWeight.normal},
        'caption': {'size': 12.0, 'weight': FontWeight.normal},
      },
    };
  }
} 