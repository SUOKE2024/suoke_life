import 'dart:async';

import '../core/agent_microkernel.dart';
import '../models/ai_agent.dart';
import '../models/ai_agent.dart';
import '../../core/utils/logger.dart';

/// 医学诊断结果
class DiagnosisResult {
  /// 诊断内容
  final String diagnosis;

  /// 诊断建议
  final String recommendation;

  /// 置信度 (0.0-1.0)
  final double confidenceLevel;

  /// 是否为中医诊断
  final bool isTraditionalChinese;

  /// 诊断时间
  final DateTime timestamp;

  /// 相关症状
  final List<String>? symptoms;

  /// 附加信息
  final Map<String, dynamic>? additionalInfo;

  DiagnosisResult({
    required this.diagnosis,
    required this.recommendation,
    required this.confidenceLevel,
    this.isTraditionalChinese = false,
    DateTime? timestamp,
    this.symptoms,
    this.additionalInfo,
  }) : timestamp = timestamp ?? DateTime.now();

  /// 从Map创建实例
  factory DiagnosisResult.fromMap(Map<String, dynamic> map) {
    return DiagnosisResult(
      diagnosis: map['diagnosis'] as String,
      recommendation: map['recommendation'] as String,
      confidenceLevel: (map['confidenceLevel'] as num).toDouble(),
      isTraditionalChinese: map['isTraditionalChinese'] as bool? ?? false,
      timestamp:
          map['timestamp'] != null
              ? DateTime.parse(map['timestamp'] as String)
              : null,
      symptoms:
          map['symptoms'] != null
              ? List<String>.from(map['symptoms'] as List)
              : null,
      additionalInfo: map['additionalInfo'] as Map<String, dynamic>?,
    );
  }

  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'diagnosis': diagnosis,
      'recommendation': recommendation,
      'confidenceLevel': confidenceLevel,
      'isTraditionalChinese': isTraditionalChinese,
      'timestamp': timestamp.toIso8601String(),
      'symptoms': symptoms,
      'additionalInfo': additionalInfo,
    };
  }
}

/// 定义协作请求类型
enum CollaborationRequestType {
  /// 数据共享请求
  dataSharing,

  /// 分析请求
  analysis,

  /// 建议请求
  recommendation,

  /// 验证请求
  validation,

  /// 联合诊断请求
  jointDiagnosis,

  /// 多模态分析请求
  multimodalAnalysis,
}

/// 代理协作结果状态
enum CollaborationResultStatus {
  /// 成功
  success,

  /// 部分成功
  partialSuccess,

  /// 失败
  failure,

  /// 拒绝
  rejected,

  /// 超时
  timeout,
}

/// 代理协作请求
class CollaborationRequest {
  /// 请求ID
  final String id;

  /// 发起代理ID
  final String initiatorId;

  /// 目标代理ID
  final String targetId;

  /// 请求类型
  final CollaborationRequestType type;

  /// 请求数据
  final Map<String, dynamic> data;

  /// 请求上下文
  final Map<String, dynamic> context;

  /// 超时时间(毫秒)
  final int timeout;

  /// 是否需要响应
  final bool requiresResponse;

  /// 创建时间
  final DateTime createdAt;

  /// 协作请求构造函数
  CollaborationRequest({
    required this.id,
    required this.initiatorId,
    required this.targetId,
    required this.type,
    required this.data,
    this.context = const {},
    this.timeout = 30000, // 默认30秒
    this.requiresResponse = true,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  /// 从AgentMessage创建
  factory CollaborationRequest.fromMessage(AgentMessage message) {
    final content = message.content;
    return CollaborationRequest(
      id: message.id,
      initiatorId: message.senderId,
      targetId: message.receiverId,
      type: CollaborationRequestType.values.firstWhere(
        (e) => e.toString() == content['requestType'],
        orElse: () => CollaborationRequestType.dataSharing,
      ),
      data: Map<String, dynamic>.from(content['data'] ?? {}),
      context: Map<String, dynamic>.from(content['context'] ?? {}),
      timeout: content['timeout'] ?? 30000,
      requiresResponse: message.requiresResponse,
      createdAt: message.timestamp,
    );
  }

  /// 转换为AgentMessage
  AgentMessage toMessage() {
    return AgentMessage(
      senderId: initiatorId,
      receiverId: targetId,
      type: AgentMessageType.query,
      priority: AgentMessagePriority.high,
      content: {
        'requestType': type.toString(),
        'data': data,
        'context': context,
        'timeout': timeout,
        'collaborationRequestId': id,
      },
      requiresResponse: requiresResponse,
    );
  }

  /// 创建响应
  CollaborationResult createResponse({
    required CollaborationResultStatus status,
    required Map<String, dynamic> resultData,
    String? message,
  }) {
    return CollaborationResult(
      requestId: id,
      initiatorId: initiatorId,
      targetId: targetId,
      status: status,
      data: resultData,
      message: message,
    );
  }
}

/// 代理协作结果
class CollaborationResult {
  /// 相关请求ID
  final String requestId;

  /// 发起代理ID
  final String initiatorId;

  /// 目标代理ID
  final String targetId;

  /// 结果状态
  final CollaborationResultStatus status;

  /// 结果数据
  final Map<String, dynamic> data;

  /// 结果消息
  final String? message;

  /// 完成时间
  final DateTime completedAt;

  /// 协作结果构造函数
  CollaborationResult({
    required this.requestId,
    required this.initiatorId,
    required this.targetId,
    required this.status,
    required this.data,
    this.message,
    DateTime? completedAt,
  }) : completedAt = completedAt ?? DateTime.now();

  /// 从AgentMessage创建
  factory CollaborationResult.fromMessage(AgentMessage message) {
    final content = message.content;
    return CollaborationResult(
      requestId: content['collaborationRequestId'],
      initiatorId: message.receiverId,
      targetId: message.senderId,
      status: CollaborationResultStatus.values.firstWhere(
        (e) => e.toString() == content['status'],
        orElse: () => CollaborationResultStatus.failure,
      ),
      data: Map<String, dynamic>.from(content['data'] ?? {}),
      message: content['message'],
      completedAt: message.timestamp,
    );
  }

  /// 转换为AgentMessage
  AgentMessage toMessage() {
    return AgentMessage(
      senderId: targetId,
      receiverId: initiatorId,
      type: AgentMessageType.response,
      priority: AgentMessagePriority.high,
      content: {
        'collaborationRequestId': requestId,
        'status': status.toString(),
        'data': data,
        'message': message,
      },
    );
  }

  /// 是否成功
  bool get isSuccess =>
      status == CollaborationResultStatus.success ||
      status == CollaborationResultStatus.partialSuccess;
}

/// 代理协作处理器
typedef CollaborationRequestHandler =
    Future<CollaborationResult> Function(CollaborationRequest request);

/// 代理协作管理器
class AgentCollaborationManager {
  final AgentMicrokernel _microkernel;
  final String _agentId;

  /// 协作请求处理器映射
  final Map<CollaborationRequestType, CollaborationRequestHandler> _handlers =
      {};

  /// 等待中的协作请求
  final Map<String, Completer<CollaborationResult>> _pendingRequests = {};

  /// 构造函数
  AgentCollaborationManager(this._microkernel, this._agentId) {
    _registerMessageSubscriber();
  }

  /// 注册消息处理器
  void _registerMessageSubscriber() {
    _microkernel.registerAgent(_agentId, _handleMessage);
  }

  /// 注册协作请求处理器
  void registerHandler(
    CollaborationRequestType requestType,
    CollaborationRequestHandler handler,
  ) {
    _handlers[requestType] = handler;
  }

  /// 处理收到的消息
  Future<void> _handleMessage(AgentMessage message) async {
    // 检查是否是协作请求
    if (message.type == AgentMessageType.query &&
        message.content.containsKey('collaborationRequestId')) {
      await _handleCollaborationRequest(message);
    }
    // 检查是否是协作响应
    else if (message.type == AgentMessageType.response &&
        message.content.containsKey('collaborationRequestId')) {
      _handleCollaborationResponse(message);
    }
  }

  /// 处理协作请求
  Future<void> _handleCollaborationRequest(AgentMessage message) async {
    final request = CollaborationRequest.fromMessage(message);

    try {
      // 获取对应类型的处理器
      final handler = _handlers[request.type];

      if (handler == null) {
        // 没有找到处理器，发送拒绝响应
        if (request.requiresResponse) {
          final result = request.createResponse(
            status: CollaborationResultStatus.rejected,
            resultData: {},
            message: '不支持的协作请求类型: ${request.type}',
          );

          await _sendCollaborationResult(result);
        }
        return;
      }

      // 处理请求
      final result = await handler(request);

      // 发送响应
      if (request.requiresResponse) {
        await _sendCollaborationResult(result);
      }
    } catch (e, stackTrace) {
      logger.e('处理协作请求失败', error: e, stackTrace: stackTrace);

      // 发送错误响应
      if (request.requiresResponse) {
        final result = request.createResponse(
          status: CollaborationResultStatus.failure,
          resultData: {},
          message: '处理请求时发生错误: $e',
        );

        await _sendCollaborationResult(result);
      }
    }
  }

  /// 处理协作响应
  void _handleCollaborationResponse(AgentMessage message) {
    final result = CollaborationResult.fromMessage(message);
    final requestId = result.requestId;

    // 检查是否有等待中的请求
    final completer = _pendingRequests[requestId];
    if (completer != null) {
      completer.complete(result);
      _pendingRequests.remove(requestId);
    } else {
      logger.w('收到未知请求的协作响应: $requestId');
    }
  }

  /// 发送协作请求
  Future<CollaborationResult> sendCollaborationRequest(
    CollaborationRequest request,
  ) async {
    if (!request.requiresResponse) {
      // 不需要响应的请求，直接发送
      await _microkernel.sendMessage(request.toMessage());

      // 返回一个空的成功结果
      return CollaborationResult(
        requestId: request.id,
        initiatorId: request.initiatorId,
        targetId: request.targetId,
        status: CollaborationResultStatus.success,
        data: {},
        message: '请求已发送，不需要响应',
      );
    }

    // 创建一个Completer，并存储到等待中的请求
    final completer = Completer<CollaborationResult>();
    _pendingRequests[request.id] = completer;

    // 设置超时
    final timeoutDuration = Duration(milliseconds: request.timeout);
    bool isCompleted = false;

    // 发送消息
    try {
      await _microkernel.sendMessage(request.toMessage());
    } catch (e, stackTrace) {
      logger.e('发送协作请求失败', error: e, stackTrace: stackTrace);
      _pendingRequests.remove(request.id);

      // 返回失败结果
      return CollaborationResult(
        requestId: request.id,
        initiatorId: request.initiatorId,
        targetId: request.targetId,
        status: CollaborationResultStatus.failure,
        data: {},
        message: '发送请求失败: $e',
      );
    }

    // 等待响应或超时
    try {
      return await completer.future.timeout(
        timeoutDuration,
        onTimeout: () {
          isCompleted = true;
          _pendingRequests.remove(request.id);

          return CollaborationResult(
            requestId: request.id,
            initiatorId: request.initiatorId,
            targetId: request.targetId,
            status: CollaborationResultStatus.timeout,
            data: {},
            message: '请求超时',
          );
        },
      );
    } catch (e) {
      if (!isCompleted) {
        _pendingRequests.remove(request.id);
      }

      // 返回失败结果
      return CollaborationResult(
        requestId: request.id,
        initiatorId: request.initiatorId,
        targetId: request.targetId,
        status: CollaborationResultStatus.failure,
        data: {},
        message: '等待响应时出错: $e',
      );
    }
  }

  /// 发送协作结果
  Future<void> _sendCollaborationResult(CollaborationResult result) async {
    try {
      await _microkernel.sendMessage(result.toMessage());
    } catch (e, stackTrace) {
      logger.e('发送协作响应失败', error: e, stackTrace: stackTrace);
    }
  }

  /// 创建数据共享请求
  CollaborationRequest createDataSharingRequest({
    required String targetAgentId,
    required Map<String, dynamic> data,
    Map<String, dynamic> context = const {},
    bool requiresResponse = true,
  }) {
    return CollaborationRequest(
      id: 'share_${DateTime.now().millisecondsSinceEpoch}_${_agentId}',
      initiatorId: _agentId,
      targetId: targetAgentId,
      type: CollaborationRequestType.dataSharing,
      data: data,
      context: context,
      requiresResponse: requiresResponse,
    );
  }

  /// 创建分析请求
  CollaborationRequest createAnalysisRequest({
    required String targetAgentId,
    required Map<String, dynamic> data,
    Map<String, dynamic> context = const {},
  }) {
    return CollaborationRequest(
      id: 'analysis_${DateTime.now().millisecondsSinceEpoch}_${_agentId}',
      initiatorId: _agentId,
      targetId: targetAgentId,
      type: CollaborationRequestType.analysis,
      data: data,
      context: context,
    );
  }

  /// 创建建议请求
  CollaborationRequest createRecommendationRequest({
    required String targetAgentId,
    required Map<String, dynamic> data,
    Map<String, dynamic> context = const {},
  }) {
    return CollaborationRequest(
      id: 'recommendation_${DateTime.now().millisecondsSinceEpoch}_${_agentId}',
      initiatorId: _agentId,
      targetId: targetAgentId,
      type: CollaborationRequestType.recommendation,
      data: data,
      context: context,
    );
  }

  /// 创建联合诊断请求
  CollaborationRequest createJointDiagnosisRequest({
    required String targetAgentId,
    required Map<String, dynamic> data,
    Map<String, dynamic> context = const {},
  }) {
    return CollaborationRequest(
      id: 'joint_diagnosis_${DateTime.now().millisecondsSinceEpoch}_${_agentId}',
      initiatorId: _agentId,
      targetId: targetAgentId,
      type: CollaborationRequestType.jointDiagnosis,
      data: data,
      context: context,
    );
  }
}
