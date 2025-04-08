// 工具接口
// 定义了智能体使用的工具接口规范

import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';

import '../models/agent_message.dart';

/// 工具参数类型
enum ToolParameterType {
  /// 字符串类型
  string,
  
  /// 整数类型
  integer,
  
  /// 数字类型（浮点数）
  number,
  
  /// 布尔类型
  boolean,
  
  /// 对象类型
  object,
  
  /// 数组类型
  array,
}

/// 工具参数定义
class ToolParameterDefinition {
  /// 参数名称
  final String name;
  
  /// 参数描述
  final String description;
  
  /// 参数类型
  final ToolParameterType type;
  
  /// 是否必需
  final bool required;
  
  /// 默认值
  final dynamic defaultValue;
  
  /// 枚举值（如果有）
  final List<dynamic>? enumValues;
  
  /// 构造函数
  const ToolParameterDefinition({
    required this.name,
    required this.description,
    required this.type,
    this.required = false,
    this.defaultValue,
    this.enumValues,
  });
  
  /// 从JSON创建
  factory ToolParameterDefinition.fromJson(Map<String, dynamic> json) {
    return ToolParameterDefinition(
      name: json['name'] as String,
      description: json['description'] as String,
      type: _parseType(json['type'] as String),
      required: json['required'] as bool? ?? false,
      defaultValue: json['default'],
      enumValues: json['enum'] != null 
          ? (json['enum'] as List).map((e) => e).toList()
          : null,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'description': description,
      'type': type.toString().split('.').last,
      'required': required,
      if (defaultValue != null) 'default': defaultValue,
      if (enumValues != null) 'enum': enumValues,
    };
  }
  
  /// 解析类型字符串
  static ToolParameterType _parseType(String typeStr) {
    switch (typeStr.toLowerCase()) {
      case 'string':
        return ToolParameterType.string;
      case 'integer':
        return ToolParameterType.integer;
      case 'number':
        return ToolParameterType.number;
      case 'boolean':
        return ToolParameterType.boolean;
      case 'object':
        return ToolParameterType.object;
      case 'array':
        return ToolParameterType.array;
      default:
        return ToolParameterType.string;
    }
  }
}

/// 工具调用结果
class ToolCallResult {
  /// 结果类型
  final bool success;
  
  /// 输出内容（文本）
  final String output;
  
  /// 错误信息
  final String? error;
  
  /// 元数据
  final Map<String, dynamic>? metadata;
  
  /// 构造函数
  const ToolCallResult({
    required this.success,
    required this.output,
    this.error,
    this.metadata,
  });
  
  /// 成功结果
  factory ToolCallResult.success(String output, {Map<String, dynamic>? metadata}) {
    return ToolCallResult(
      success: true,
      output: output,
      metadata: metadata,
    );
  }
  
  /// 失败结果
  factory ToolCallResult.failure(String error, {Map<String, dynamic>? metadata}) {
    return ToolCallResult(
      success: false,
      output: error,
      error: error,
      metadata: metadata,
    );
  }
  
  /// 转换为代理消息
  AgentMessage toAgentMessage() {
    if (success) {
      final content = output is String 
          ? output 
          : (output != null ? jsonEncode(output) : '操作成功');
      return AgentMessage.toolResult(
        content: content,
        toolCallId: metadata?['id'] as String?,
      );
    } else {
      return AgentMessage.toolResult(
        content: error ?? '操作失败',
        toolCallId: metadata?['id'] as String?,
        status: AgentMessageStatus.error,
      );
    }
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'success': success,
      'output': output,
      if (error != null) 'error': error,
      if (metadata != null) ...metadata!,
    };
  }
  
  @override
  String toString() {
    return jsonEncode(toJson());
  }
}

/// 工具接口
abstract class Tool {
  /// 获取工具名称
  String getName();
  
  /// 获取工具描述
  String getDescription();
  
  /// 获取工具参数定义
  Map<String, ToolParameterDefinition> getParameters();
  
  /// 工具是否需要认证
  bool requiresAuthentication();
  
  /// 获取工具OpenAI格式定义
  Map<String, dynamic> getDefinition();
  
  /// 执行工具
  Future<ToolCallResult> execute(Map<String, dynamic> parameters);
  
  /// 验证参数
  bool validateParameters(Map<String, dynamic> params) {
    // 检查所有必需的参数是否存在
    for (final param in getParameters().values.where((p) => p.required)) {
      if (!params.containsKey(param.name) && param.defaultValue == null) {
        return false;
      }
    }
    return true;
  }
}

/// 工具注册表
class ToolRegistry {
  /// 单例实例
  static final ToolRegistry _instance = ToolRegistry._internal();
  
  /// 获取单例实例
  factory ToolRegistry() {
    return _instance;
  }
  
  /// 内部构造函数
  ToolRegistry._internal();
  
  /// 已注册的工具实例
  final Map<String, Tool> _tools = {};
  
  /// 注册工具
  void registerTool(Tool tool) {
    _tools[tool.getName()] = tool;
    if (kDebugMode) {
      print('已注册工具: ${tool.getName()}');
    }
  }
  
  /// 注销工具
  void unregisterTool(String toolName) {
    _tools.remove(toolName);
  }
  
  /// 获取所有工具
  List<Tool> get tools => _tools.values.toList();
  
  /// 获取所有工具定义
  List<Map<String, dynamic>> get toolDefinitions {
    return tools.map((tool) => tool.getDefinition()).toList();
  }
  
  /// 获取工具
  Tool? getTool(String name) {
    return _tools[name];
  }
  
  /// 执行工具调用
  Future<ToolCallResult> executeToolCall(
    String toolName, 
    Map<String, dynamic> parameters,
    [String? callId]
  ) async {
    final tool = getTool(toolName);
    
    if (tool == null) {
      return ToolCallResult.failure(
        '未找到工具: $toolName',
        metadata: {'id': callId},
      );
    }
    
    // 验证参数
    if (!tool.validateParameters(parameters)) {
      return ToolCallResult.failure(
        '工具参数无效: ${tool.getName()}',
        metadata: {'id': callId},
      );
    }
    
    try {
      // 添加默认值
      final paramsWithDefaults = Map<String, dynamic>.from(parameters);
      for (final param in tool.getParameters().values) {
        if (!paramsWithDefaults.containsKey(param.name) && param.defaultValue != null) {
          paramsWithDefaults[param.name] = param.defaultValue;
        }
      }
      
      final result = await tool.execute(paramsWithDefaults);
      
      // 确保结果ID与调用ID一致
      if (callId != null && result.metadata?['id'] != callId) {
        return ToolCallResult(
          success: result.success,
          output: result.output,
          error: result.error,
          metadata: {
            ...result.metadata!,
            'id': callId,
          },
        );
      }
      
      return result;
    } catch (e) {
      return ToolCallResult.failure(
        '工具执行错误: ${e.toString()}',
        metadata: {'id': callId},
      );
    }
  }
} 