// 工具注册表类
// 用于管理和执行智能体使用的工具

import 'dart:async';
import 'dart:collection';
import 'dart:convert';
import '../utils/logger.dart';

import 'package:logger/logger.dart' as log_pkg;
import 'package:suoke_life/core/utils/logger.dart';

import 'tool_interface.dart';

/// 工具函数类型定义
typedef ToolFunction = Future<Map<String, dynamic>> Function(Map<String, dynamic> params);

/// 工具参数类型定义
enum ToolParamType {
  string,  // 字符串
  number,  // 数字
  boolean, // 布尔值
  object,  // 对象
  array    // 数组
}

/// 工具参数定义
class ToolParameter {
  /// 参数名称
  final String name;
  
  /// 参数描述
  final String description;
  
  /// 参数类型
  final ToolParamType type;
  
  /// 是否必需
  final bool required;
  
  /// 默认值
  final dynamic defaultValue;
  
  /// 可用选项（对于枚举参数）
  final List<dynamic>? enumValues;
  
  /// 构造函数
  const ToolParameter({
    required this.name,
    required this.description,
    required this.type,
    this.required = false,
    this.defaultValue,
    this.enumValues,
  });
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'name': name,
      'description': description,
      'type': _typeToString(type),
      'required': required,
      if (defaultValue != null) 'default': defaultValue,
      if (enumValues != null) 'enum': enumValues,
    };
  }
  
  /// 类型转换为字符串
  static String _typeToString(ToolParamType type) {
    switch (type) {
      case ToolParamType.string:
        return 'string';
      case ToolParamType.number:
        return 'number';
      case ToolParamType.boolean:
        return 'boolean';
      case ToolParamType.object:
        return 'object';
      case ToolParamType.array:
        return 'array';
    }
  }
}

/// 工具定义
class Tool {
  /// 工具名称
  final String name;
  
  /// 工具描述
  final String description;
  
  /// 工具参数
  final List<ToolParameter> parameters;
  
  /// 工具函数
  final ToolFunction function;
  
  /// 构造函数
  const Tool({
    required this.name,
    required this.description,
    required this.parameters,
    required this.function,
  });
  
  /// 执行工具
  Future<Map<String, dynamic>> execute(Map<String, dynamic> params) async {
    // 验证必需参数
    for (final param in parameters.where((p) => p.required)) {
      if (!params.containsKey(param.name) || params[param.name] == null) {
        throw ArgumentError('缺少必需参数: ${param.name}');
      }
    }
    
    // 添加默认值
    for (final param in parameters.where((p) => p.defaultValue != null)) {
      if (!params.containsKey(param.name) || params[param.name] == null) {
        params[param.name] = param.defaultValue;
      }
    }
    
    try {
      // 执行工具函数
      final result = await function(params);
      return result;
    } catch (e, stackTrace) {
      LoggerUtil.error('工具执行错误: ${e.toString()}', e, stackTrace);
      return {
        'error': '工具执行失败',
        'message': e.toString(),
      };
    }
  }
  
  /// 转换为OpenAI工具格式
  Map<String, dynamic> toOpenAIToolFormat() {
    final paramProperties = <String, dynamic>{};
    final requiredParams = <String>[];
    
    for (final param in parameters) {
      paramProperties[param.name] = param.toMap();
      if (param.required) {
        requiredParams.add(param.name);
      }
    }
    
    return {
      'type': 'function',
      'function': {
        'name': name,
        'description': description,
        'parameters': {
          'type': 'object',
          'properties': paramProperties,
          'required': requiredParams,
        },
      },
    };
  }
}

/// 工具注册表类
/// 支持OpenAI Assistants API样式的工具定义
class ToolRegistry {
  static final Logger _logger = Logger('ToolRegistry');

  /// 已注册的工具
  final Map<String, Tool> _tools = HashMap<String, Tool>();

  /// 构造函数
  ToolRegistry({List<Tool>? tools}) {
    if (tools != null) {
      registerTools(tools);
    }
  }

  /// 注册单个工具
  void registerTool(Tool tool) {
    final name = tool.name;
    
    if (_tools.containsKey(name)) {
      _logger.warning('工具 "$name" 已存在，将被覆盖');
    }
    
    _tools[name] = tool;
    _logger.info('已注册工具: $name');
  }

  /// 批量注册工具
  void registerTools(List<Tool> tools) {
    for (final tool in tools) {
      registerTool(tool);
    }
  }

  /// 取消注册工具
  bool unregisterTool(String name) {
    if (_tools.containsKey(name)) {
      _tools.remove(name);
      _logger.info('已取消注册工具: $name');
      return true;
    }
    
    _logger.warning('尝试取消注册不存在的工具: $name');
    return false;
  }

  /// 获取工具（如果存在）
  Tool? getTool(String name) {
    return _tools[name];
  }

  /// 获取所有已注册工具
  List<Tool> getAllTools() {
    return _tools.values.toList();
  }

  /// 获取工具定义列表（用于LLM API）
  List<Map<String, dynamic>> getToolDefinitions() {
    return _tools.values.map((tool) => tool.toOpenAIToolFormat()).toList();
  }

  /// 筛选特定工具
  List<Tool> filterTools({List<String>? allowedTools, List<String>? prohibitedTools}) {
    var filteredTools = _tools.values.toList();
    
    if (allowedTools != null && allowedTools.isNotEmpty) {
      filteredTools = filteredTools
          .where((tool) => allowedTools.contains(tool.name))
          .toList();
    }
    
    if (prohibitedTools != null && prohibitedTools.isNotEmpty) {
      filteredTools = filteredTools
          .where((tool) => !prohibitedTools.contains(tool.name))
          .toList();
    }
    
    return filteredTools;
  }

  /// 执行工具调用
  Future<ToolCallResult> executeToolCall(String toolName, Map<String, dynamic> parameters) async {
    final stopwatch = Stopwatch()..start();
    
    try {
      final tool = getTool(toolName);
      
      if (tool == null) {
        _logger.error('工具未找到: $toolName');
        return ToolCallResult.failure('工具 "$toolName" 未注册或不可用');
      }
      
      _logger.info('执行工具: $toolName, 参数: $parameters');
      
      final result = await tool.execute(parameters);
      
      final elapsedMs = stopwatch.elapsedMilliseconds;
      _logger.info('工具 $toolName 执行完成，耗时 ${elapsedMs}ms');
      
      return result;
    } catch (e, stackTrace) {
      final elapsedMs = stopwatch.elapsedMilliseconds;
      _logger.error('执行工具 $toolName 失败，耗时 ${elapsedMs}ms: $e', stackTrace);
      return ToolCallResult.failure('执行工具时发生错误: $e');
    }
  }

  /// 检查服务是否可用
  bool isAvailable(String toolName) {
    final tool = getTool(toolName);
    return tool != null;
  }
  
  /// 根据启用工具列表获取工具定义
  List<Map<String, dynamic>> getEnabledToolDefinitions(List<String> enabledTools) {
    return filterTools(allowedTools: enabledTools)
        .map((tool) => tool.toOpenAIToolFormat())
        .toList();
  }
}