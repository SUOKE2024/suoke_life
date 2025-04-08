// 智能体响应模型类
// 表示智能体对用户请求的响应

import 'package:flutter/foundation.dart';

/// 智能体动作类型
enum AgentActionType {
  text,           // 纯文本响应
  recommendation, // 推荐内容
  healthPlan,     // 健康计划
  diagnosis,      // 诊断结果
  productInfo,    // 产品信息
  farmExperience, // 农事体验
  reminder,       // 健康提醒
  alert           // 健康预警
}

/// 智能体动作
@immutable
class AgentAction {
  /// 动作类型
  final AgentActionType type;
  
  /// 动作标题
  final String title;
  
  /// 动作内容
  final Map<String, dynamic> data;
  
  /// 构造函数
  const AgentAction({
    required this.type,
    required this.title,
    required this.data,
  });
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'type': type.toString().split('.').last,
      'title': title,
      'data': data,
    };
  }
  
  /// 从Map创建实例
  factory AgentAction.fromMap(Map<String, dynamic> map) {
    return AgentAction(
      type: _typeFromString(map['type']),
      title: map['title'],
      data: map['data'],
    );
  }
  
  /// 从字符串解析动作类型
  static AgentActionType _typeFromString(String typeString) {
    switch (typeString) {
      case 'text':
        return AgentActionType.text;
      case 'recommendation':
        return AgentActionType.recommendation;
      case 'healthPlan':
        return AgentActionType.healthPlan;
      case 'diagnosis':
        return AgentActionType.diagnosis;
      case 'productInfo':
        return AgentActionType.productInfo;
      case 'farmExperience':
        return AgentActionType.farmExperience;
      case 'reminder':
        return AgentActionType.reminder;
      case 'alert':
        return AgentActionType.alert;
      default:
        return AgentActionType.text;
    }
  }
}

/// 智能体响应类
@immutable
class AgentResponse {
  /// 响应文本
  final String text;
  
  /// 响应ID
  final String id;
  
  /// 响应时间戳
  final DateTime timestamp;
  
  /// 智能体动作列表
  final List<AgentAction>? actions;
  
  /// 智能体类型
  final String? agentType;
  
  /// 是否成功
  final bool success;
  
  /// 错误代码
  final String? errorCode;
  
  /// 错误信息
  final String? errorMessage;
  
  /// 响应源
  final String? source;
  
  /// 元数据
  final Map<String, dynamic>? metadata;
  
  /// 构造函数
  AgentResponse({
    required this.text,
    String? id,
    DateTime? timestamp,
    this.actions,
    this.agentType,
    this.success = true,
    this.errorCode,
    this.errorMessage,
    this.source,
    this.metadata,
  }) : 
    this.id = id ?? DateTime.now().millisecondsSinceEpoch.toString(),
    this.timestamp = timestamp ?? DateTime.now();
  
  /// 创建成功响应
  factory AgentResponse.success({
    required String text,
    List<AgentAction>? actions,
    String? agentType,
    String? source,
    Map<String, dynamic>? metadata,
  }) {
    return AgentResponse(
      text: text,
      actions: actions,
      agentType: agentType,
      success: true,
      source: source,
      metadata: metadata,
    );
  }
  
  /// 创建错误响应
  factory AgentResponse.error({
    required String text,
    required String errorCode,
    String? errorMessage,
    String? agentType,
  }) {
    return AgentResponse(
      text: text,
      success: false,
      errorCode: errorCode,
      errorMessage: errorMessage,
      agentType: agentType,
    );
  }
  
  /// 判断是否有错误
  bool get hasError => !success;
  
  /// 判断是否有动作
  bool get hasActions => actions != null && actions!.isNotEmpty;
  
  /// 复制并修改响应
  AgentResponse copyWith({
    String? text,
    String? id,
    DateTime? timestamp,
    List<AgentAction>? actions,
    String? agentType,
    bool? success,
    String? errorCode,
    String? errorMessage,
    String? source,
    Map<String, dynamic>? metadata,
  }) {
    return AgentResponse(
      text: text ?? this.text,
      id: id ?? this.id,
      timestamp: timestamp ?? this.timestamp,
      actions: actions ?? this.actions,
      agentType: agentType ?? this.agentType,
      success: success ?? this.success,
      errorCode: errorCode ?? this.errorCode,
      errorMessage: errorMessage ?? this.errorMessage,
      source: source ?? this.source,
      metadata: metadata ?? this.metadata,
    );
  }
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'text': text,
      'id': id,
      'timestamp': timestamp.toIso8601String(),
      if (actions != null) 'actions': actions!.map((a) => a.toMap()).toList(),
      if (agentType != null) 'agentType': agentType,
      'success': success,
      if (errorCode != null) 'errorCode': errorCode,
      if (errorMessage != null) 'errorMessage': errorMessage,
      if (source != null) 'source': source,
      if (metadata != null) 'metadata': metadata,
    };
  }
  
  /// 从Map创建实例
  factory AgentResponse.fromMap(Map<String, dynamic> map) {
    return AgentResponse(
      text: map['text'],
      id: map['id'],
      timestamp: DateTime.parse(map['timestamp']),
      actions: map['actions'] != null 
        ? List<AgentAction>.from(map['actions'].map((x) => AgentAction.fromMap(x)))
        : null,
      agentType: map['agentType'],
      success: map['success'] ?? true,
      errorCode: map['errorCode'],
      errorMessage: map['errorMessage'],
      source: map['source'],
      metadata: map['metadata'],
    );
  }
  
  @override
  String toString() => 'AgentResponse{id: $id, success: $success, text: $text}';
  
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is AgentResponse &&
        other.id == id &&
        other.text == text &&
        other.success == success;
  }
  
  @override
  int get hashCode => id.hashCode ^ text.hashCode ^ success.hashCode;
}
