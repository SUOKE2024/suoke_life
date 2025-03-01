import 'dart:async';
import 'dart:collection';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';

import '../../core/utils/logger.dart';
import '../models/ai_agent.dart';
import 'agent_registry.dart';
import 'autonomous_learning_system.dart';

/// 代理消息类型
enum AgentMessageType {
  /// 查询请求
  query,
  
  /// 响应
  response,
  
  /// 任务分配
  taskAssignment,
  
  /// 任务进度更新
  progressUpdate,
  
  /// 任务完成
  taskCompletion,
  
  /// 错误
  error,
  
  /// 内部状态更新
  stateUpdate,
  
  /// 系统广播
  broadcast,
}

/// 代理消息优先级
enum AgentMessagePriority {
  /// 低优先级
  low,
  
  /// 中等优先级
  medium,
  
  /// 高优先级
  high,
  
  /// 紧急优先级
  urgent,
}

/// 代理间通信消息
class AgentMessage {
  /// 消息唯一ID
  final String id;
  
  /// 发送者代理ID
  final String senderId;
  
  /// 接收者代理ID
  final String receiverId;
  
  /// 消息类型
  final AgentMessageType type;
  
  /// 消息优先级
  final AgentMessagePriority priority;
  
  /// 消息内容
  final Map<String, dynamic> content;
  
  /// 相关任务ID（如果有）
  final String? taskId;
  
  /// 创建时间戳
  final DateTime timestamp;
  
  /// 消息是否需要响应
  final bool requiresResponse;
  
  /// 父消息ID（如果是响应消息）
  final String? parentMessageId;
  
  /// 过期时间
  final DateTime? expiresAt;
  
  /// 路由跟踪（消息经过的代理）
  final List<String> routingTrace;

  AgentMessage({
    String? id,
    required this.senderId,
    required this.receiverId,
    required this.type,
    this.priority = AgentMessagePriority.medium,
    required this.content,
    this.taskId,
    DateTime? timestamp,
    this.requiresResponse = false,
    this.parentMessageId,
    this.expiresAt,
    List<String>? routingTrace,
  }) : 
    id = id ?? const Uuid().v4(),
    timestamp = timestamp ?? DateTime.now(),
    routingTrace = routingTrace ?? [senderId];
  
  /// 创建响应消息
  AgentMessage createResponse({
    required String responderId,
    required Map<String, dynamic> responseContent,
    AgentMessagePriority? responsePriority,
  }) {
    return AgentMessage(
      senderId: responderId,
      receiverId: senderId,
      type: AgentMessageType.response,
      priority: responsePriority ?? priority,
      content: responseContent,
      taskId: taskId,
      parentMessageId: id,
      routingTrace: [...routingTrace, responderId],
    );
  }
  
  /// 转发消息到另一个代理
  AgentMessage forward({
    required String newReceiverId,
    Map<String, dynamic>? additionalContent,
    String? forwarderId,
  }) {
    final forwarded = AgentMessage(
      senderId: forwarderId ?? receiverId,
      receiverId: newReceiverId,
      type: type,
      priority: priority,
      content: {
        ...content,
        ...?additionalContent,
        'forwarded': true,
        'originalSenderId': senderId,
      },
      taskId: taskId,
      parentMessageId: id,
      requiresResponse: requiresResponse,
      expiresAt: expiresAt,
      routingTrace: [...routingTrace, forwarderId ?? receiverId],
    );
    
    return forwarded;
  }
  
  /// 消息是否已过期
  bool get isExpired {
    if (expiresAt == null) return false;
    return DateTime.now().isAfter(expiresAt!);
  }
  
  /// 转换为映射
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'senderId': senderId,
      'receiverId': receiverId,
      'type': type.toString(),
      'priority': priority.toString(),
      'content': content,
      'taskId': taskId,
      'timestamp': timestamp.toIso8601String(),
      'requiresResponse': requiresResponse,
      'parentMessageId': parentMessageId,
      'expiresAt': expiresAt?.toIso8601String(),
      'routingTrace': routingTrace,
    };
  }
  
  /// 从映射创建
  factory AgentMessage.fromMap(Map<String, dynamic> map) {
    return AgentMessage(
      id: map['id'],
      senderId: map['senderId'],
      receiverId: map['receiverId'],
      type: AgentMessageType.values.firstWhere(
        (e) => e.toString() == map['type'],
        orElse: () => AgentMessageType.query,
      ),
      priority: AgentMessagePriority.values.firstWhere(
        (e) => e.toString() == map['priority'],
        orElse: () => AgentMessagePriority.medium,
      ),
      content: Map<String, dynamic>.from(map['content']),
      taskId: map['taskId'],
      timestamp: DateTime.parse(map['timestamp']),
      requiresResponse: map['requiresResponse'] ?? false,
      parentMessageId: map['parentMessageId'],
      expiresAt: map['expiresAt'] != null 
        ? DateTime.parse(map['expiresAt']) 
        : null,
      routingTrace: List<String>.from(map['routingTrace'] ?? []),
    );
  }
  
  /// 转换为JSON
  String toJson() => jsonEncode(toMap());
  
  /// 从JSON创建
  factory AgentMessage.fromJson(String source) => 
      AgentMessage.fromMap(jsonDecode(source));
  
  @override
  String toString() {
    return 'AgentMessage(id: $id, type: $type, from: $senderId, to: $receiverId)';
  }
}

/// 代理任务状态
enum AgentTaskStatus {
  /// 等待中
  pending,
  
  /// 进行中
  inProgress,
  
  /// 已完成
  completed,
  
  /// 失败
  failed,
  
  /// 已取消
  cancelled,
}

/// 代理任务
class AgentTask {
  /// 任务唯一ID
  final String id;
  
  /// 任务标题
  final String title;
  
  /// 任务描述
  final String description;
  
  /// 任务创建者
  final String createdBy;
  
  /// 主负责代理
  final String assignedTo;
  
  /// 协作代理列表
  final List<String> collaborators;
  
  /// 任务参数
  final Map<String, dynamic> parameters;
  
  /// 任务状态
  AgentTaskStatus status;
  
  /// 任务进度 (0.0 - 1.0)
  double progress;
  
  /// 任务结果
  Map<String, dynamic>? result;
  
  /// 错误信息（如果失败）
  String? errorMessage;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 开始时间
  DateTime? startedAt;
  
  /// 完成时间
  DateTime? completedAt;
  
  /// 截止时间
  final DateTime? deadline;
  
  /// 任务子步骤
  final List<AgentTask> subtasks;
  
  /// 父任务ID（如果是子任务）
  final String? parentTaskId;
  
  /// 任务优先级
  final int priority;
  
  /// 相关消息历史ID
  final List<String> relatedMessageIds;
  
  AgentTask({
    String? id,
    required this.title,
    required this.description,
    required this.createdBy,
    required this.assignedTo,
    List<String>? collaborators,
    Map<String, dynamic>? parameters,
    this.status = AgentTaskStatus.pending,
    this.progress = 0.0,
    this.result,
    this.errorMessage,
    DateTime? createdAt,
    this.startedAt,
    this.completedAt,
    this.deadline,
    List<AgentTask>? subtasks,
    this.parentTaskId,
    this.priority = 0,
    List<String>? relatedMessageIds,
  }) : 
    id = id ?? const Uuid().v4(),
    collaborators = collaborators ?? [],
    parameters = parameters ?? {},
    createdAt = createdAt ?? DateTime.now(),
    subtasks = subtasks ?? [],
    relatedMessageIds = relatedMessageIds ?? [];
  
  /// 标记任务开始
  void start() {
    status = AgentTaskStatus.inProgress;
    startedAt = DateTime.now();
  }
  
  /// 更新任务进度
  void updateProgress(double newProgress) {
    progress = newProgress.clamp(0.0, 1.0);
    if (progress >= 1.0 && status == AgentTaskStatus.inProgress) {
      complete({});
    }
  }
  
  /// 标记任务完成
  void complete(Map<String, dynamic> taskResult) {
    status = AgentTaskStatus.completed;
    progress = 1.0;
    result = taskResult;
    completedAt = DateTime.now();
  }
  
  /// 标记任务失败
  void fail(String error) {
    status = AgentTaskStatus.failed;
    errorMessage = error;
    completedAt = DateTime.now();
  }
  
  /// 取消任务
  void cancel() {
    status = AgentTaskStatus.cancelled;
    completedAt = DateTime.now();
  }
  
  /// 添加相关消息
  void addRelatedMessage(String messageId) {
    if (!relatedMessageIds.contains(messageId)) {
      relatedMessageIds.add(messageId);
    }
  }
  
  /// 添加子任务
  void addSubtask(AgentTask subtask) {
    subtasks.add(subtask);
  }
  
  /// 任务是否已截止
  bool get isOverdue {
    if (deadline == null) return false;
    if (status == AgentTaskStatus.completed || 
        status == AgentTaskStatus.cancelled) return false;
    return DateTime.now().isAfter(deadline!);
  }
  
  /// 转换为映射
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'createdBy': createdBy,
      'assignedTo': assignedTo,
      'collaborators': collaborators,
      'parameters': parameters,
      'status': status.toString(),
      'progress': progress,
      'result': result,
      'errorMessage': errorMessage,
      'createdAt': createdAt.toIso8601String(),
      'startedAt': startedAt?.toIso8601String(),
      'completedAt': completedAt?.toIso8601String(),
      'deadline': deadline?.toIso8601String(),
      'subtasks': subtasks.map((e) => e.toMap()).toList(),
      'parentTaskId': parentTaskId,
      'priority': priority,
      'relatedMessageIds': relatedMessageIds,
    };
  }
  
  /// 从映射创建
  factory AgentTask.fromMap(Map<String, dynamic> map) {
    return AgentTask(
      id: map['id'],
      title: map['title'],
      description: map['description'],
      createdBy: map['createdBy'],
      assignedTo: map['assignedTo'],
      collaborators: List<String>.from(map['collaborators'] ?? []),
      parameters: Map<String, dynamic>.from(map['parameters'] ?? {}),
      status: AgentTaskStatus.values.firstWhere(
        (e) => e.toString() == map['status'],
        orElse: () => AgentTaskStatus.pending,
      ),
      progress: map['progress'] ?? 0.0,
      result: map['result'],
      errorMessage: map['errorMessage'],
      createdAt: DateTime.parse(map['createdAt']),
      startedAt: map['startedAt'] != null ? DateTime.parse(map['startedAt']) : null,
      completedAt: map['completedAt'] != null ? DateTime.parse(map['completedAt']) : null,
      deadline: map['deadline'] != null ? DateTime.parse(map['deadline']) : null,
      subtasks: (map['subtasks'] as List?)
          ?.map((e) => AgentTask.fromMap(e))
          .toList() ?? [],
      parentTaskId: map['parentTaskId'],
      priority: map['priority'] ?? 0,
      relatedMessageIds: List<String>.from(map['relatedMessageIds'] ?? []),
    );
  }
  
  /// 转换为JSON
  String toJson() => jsonEncode(toMap());
  
  /// 从JSON创建
  factory AgentTask.fromJson(String source) => 
      AgentTask.fromMap(jsonDecode(source));
}

/// 消息总线策略
enum MessageBusStrategy {
  /// 先进先出（默认）
  fifo,
  
  /// 基于优先级
  priorityBased,
  
  /// 基于主题
  topicBased,
  
  /// 广播模式
  broadcast,
}

/// 消息订阅者
typedef MessageSubscriber = Future<void> Function(AgentMessage message);

/// 消息过滤器
typedef MessageFilter = bool Function(AgentMessage message);

/// 任务观察者
typedef TaskObserver = void Function(AgentTask task);

/// 代理微内核接口
abstract class AgentMicrokernel {
  /// 发送消息到特定代理
  Future<String> sendMessage(AgentMessage message);
  
  /// 广播消息到所有代理或特定组代理
  Future<List<String>> broadcastMessage(
    AgentMessage message, {
    List<String>? targetAgents,
  });
  
  /// 注册代理以接收消息
  void registerAgent(String agentId, MessageSubscriber subscriber);
  
  /// 取消注册代理
  void unregisterAgent(String agentId);
  
  /// 创建新任务
  AgentTask createTask({
    required String title,
    required String description,
    required String createdBy,
    required String assignedTo,
    List<String>? collaborators,
    Map<String, dynamic>? parameters,
    DateTime? deadline,
    int priority = 0,
  });
  
  /// 分配任务给代理
  Future<bool> assignTask(AgentTask task);
  
  /// 更新任务状态
  void updateTask(AgentTask task);
  
  /// 添加任务观察者
  void addTaskObserver(String taskId, TaskObserver observer);
  
  /// 移除任务观察者
  void removeTaskObserver(String taskId, TaskObserver observer);
  
  /// 查询任务状态
  AgentTask? getTask(String taskId);
  
  /// 获取代理的活跃任务
  List<AgentTask> getAgentTasks(String agentId);
  
  /// 中断或取消任务
  Future<bool> cancelTask(String taskId);
  
  /// 注册消息过滤器
  String registerMessageFilter(MessageFilter filter);
  
  /// 取消注册消息过滤器
  void unregisterMessageFilter(String filterId);
  
  /// 获取代理消息历史
  List<AgentMessage> getAgentMessageHistory({
    String? agentId,
    DateTime? since,
    int? limit,
    AgentMessageType? type,
  });
  
  /// 获取等待响应的消息
  List<AgentMessage> getPendingResponseMessages(String agentId);
  
  /// 清理代理的消息历史
  void clearAgentMessageHistory(String agentId, {DateTime? before});
  
  /// 监控集群健康状态，返回活跃代理数
  int getActiveAgentsCount();
  
  /// 设置消息总线策略
  void setMessageBusStrategy(MessageBusStrategy strategy);
}

/// 默认代理微内核实现
class DefaultAgentMicrokernel implements AgentMicrokernel {
  final AgentRegistry _agentRegistry;
  final AutonomousLearningSystem _learningSystem;
  
  /// 消息订阅者映射
  final Map<String, MessageSubscriber> _messageSubscribers = {};
  
  /// 消息过滤器映射
  final Map<String, MessageFilter> _messageFilters = {};
  
  /// 任务字典
  final Map<String, AgentTask> _tasks = {};
  
  /// 代理任务映射（代理ID -> 任务ID列表）
  final Map<String, Set<String>> _agentTasks = {};
  
  /// 任务观察者映射（任务ID -> 观察者列表）
  final Map<String, List<TaskObserver>> _taskObservers = {};
  
  /// 消息历史（限制大小）
  final LinkedHashMap<String, AgentMessage> _messageHistory = 
      LinkedHashMap<String, AgentMessage>();
  
  /// 消息总线策略
  MessageBusStrategy _messageBusStrategy = MessageBusStrategy.priorityBased;
  
  /// 最大历史消息数
  static const int _maxHistorySize = 1000;
  
  DefaultAgentMicrokernel(this._agentRegistry, this._learningSystem);
  
  @override
  Future<String> sendMessage(AgentMessage message) async {
    // 验证消息
    if (message.isExpired) {
      logger.w('消息已过期，不发送：$message');
      return message.id;
    }
    
    // 应用消息过滤器
    for (final filter in _messageFilters.values) {
      if (!filter(message)) {
        logger.i('消息被过滤器拦截：$message');
        return message.id;
      }
    }
    
    // 添加到历史
    _addToHistory(message);
    
    // 检查接收者是否注册
    final subscriber = _messageSubscribers[message.receiverId];
    if (subscriber == null) {
      logger.w('接收代理未注册：${message.receiverId}');
      return message.id;
    }
    
    // 投递消息
    try {
      await subscriber(message);
      
      // 收集学习数据
      await _learningSystem.collectData(LearningDataItem(
        id: 'msg_${message.id}',
        type: LearningDataType.agentCommunication,
        source: LearningDataSource.internalSystem,
        content: message.toMap(),
        timestamp: DateTime.now(),
      ));
      
    } catch (e, stackTrace) {
      logger.e('消息投递失败', error: e, stackTrace: stackTrace);
      
      // 如果需要响应，发送错误响应
      if (message.requiresResponse) {
        final errorResponse = message.createResponse(
          responderId: 'system.microkernel',
          responseContent: {
            'error': 'Message delivery failed: $e',
            'success': false,
          },
        );
        
        // 通知发送者
        final senderSubscriber = _messageSubscribers[message.senderId];
        if (senderSubscriber != null) {
          try {
            await senderSubscriber(errorResponse);
          } catch (e) {
            logger.e('错误响应投递失败：$e');
          }
        }
      }
    }
    
    return message.id;
  }
  
  @override
  Future<List<String>> broadcastMessage(
    AgentMessage message, {
    List<String>? targetAgents,
  }) async {
    final messageIds = <String>[];
    final targets = targetAgents ?? _messageSubscribers.keys.toList();
    
    // 创建广播消息的副本并发送给每个目标
    for (final agentId in targets) {
      if (agentId == message.senderId) continue; // 不发送给自己
      
      final broadcastCopy = AgentMessage(
        senderId: message.senderId,
        receiverId: agentId,
        type: AgentMessageType.broadcast,
        priority: message.priority,
        content: message.content,
        taskId: message.taskId,
        requiresResponse: message.requiresResponse,
        routingTrace: [...message.routingTrace],
      );
      
      final messageId = await sendMessage(broadcastCopy);
      messageIds.add(messageId);
    }
    
    return messageIds;
  }
  
  @override
  void registerAgent(String agentId, MessageSubscriber subscriber) {
    _messageSubscribers[agentId] = subscriber;
    logger.i('代理已注册：$agentId');
  }
  
  @override
  void unregisterAgent(String agentId) {
    _messageSubscribers.remove(agentId);
    logger.i('代理已注销：$agentId');
  }
  
  @override
  AgentTask createTask({
    required String title,
    required String description,
    required String createdBy,
    required String assignedTo,
    List<String>? collaborators,
    Map<String, dynamic>? parameters,
    DateTime? deadline,
    int priority = 0,
  }) {
    final task = AgentTask(
      title: title,
      description: description,
      createdBy: createdBy,
      assignedTo: assignedTo,
      collaborators: collaborators,
      parameters: parameters,
      deadline: deadline,
      priority: priority,
    );
    
    _tasks[task.id] = task;
    
    logger.i('创建任务: ${task.id} - $title');
    return task;
  }
  
  @override
  Future<bool> assignTask(AgentTask task) async {
    // 验证代理是否注册
    if (!_messageSubscribers.containsKey(task.assignedTo)) {
      logger.w('无法分配任务：代理未注册 - ${task.assignedTo}');
      return false;
    }
    
    // 更新任务记录
    _tasks[task.id] = task;
    
    // 更新代理任务映射
    _agentTasks.putIfAbsent(task.assignedTo, () => {}).add(task.id);
    
    // 为合作者也添加任务引用
    for (final collaborator in task.collaborators) {
      _agentTasks.putIfAbsent(collaborator, () => {}).add(task.id);
    }
    
    // 发送任务分配消息
    final taskMessage = AgentMessage(
      senderId: 'system.microkernel',
      receiverId: task.assignedTo,
      type: AgentMessageType.taskAssignment,
      content: {
        'task': task.toMap(),
        'action': 'assign',
      },
      taskId: task.id,
      requiresResponse: true,
    );
    
    await sendMessage(taskMessage);
    
    // 通知协作者
    for (final collaborator in task.collaborators) {
      final collaboratorMessage = AgentMessage(
        senderId: 'system.microkernel',
        receiverId: collaborator,
        type: AgentMessageType.taskAssignment,
        content: {
          'task': task.toMap(),
          'action': 'collaborate',
        },
        taskId: task.id,
      );
      
      await sendMessage(collaboratorMessage);
    }
    
    logger.i('任务已分配: ${task.id} 到 ${task.assignedTo}');
    return true;
  }
  
  @override
  void updateTask(AgentTask task) {
    final existingTask = _tasks[task.id];
    if (existingTask == null) {
      logger.w('无法更新：任务不存在 - ${task.id}');
      return;
    }
    
    // 更新任务
    _tasks[task.id] = task;
    
    // 通知观察者
    final observers = _taskObservers[task.id] ?? [];
    for (final observer in observers) {
      try {
        observer(task);
      } catch (e) {
        logger.w('任务观察者通知失败: $e');
      }
    }
    
    logger.i('任务已更新: ${task.id} - 状态: ${task.status}, 进度: ${task.progress}');
  }
  
  @override
  void addTaskObserver(String taskId, TaskObserver observer) {
    _taskObservers.putIfAbsent(taskId, () => []).add(observer);
  }
  
  @override
  void removeTaskObserver(String taskId, TaskObserver observer) {
    final observers = _taskObservers[taskId];
    if (observers != null) {
      observers.remove(observer);
      if (observers.isEmpty) {
        _taskObservers.remove(taskId);
      }
    }
  }
  
  @override
  AgentTask? getTask(String taskId) {
    return _tasks[taskId];
  }
  
  @override
  List<AgentTask> getAgentTasks(String agentId) {
    final taskIds = _agentTasks[agentId] ?? {};
    return taskIds.map((id) => _tasks[id]).whereType<AgentTask>().toList();
  }
  
  @override
  Future<bool> cancelTask(String taskId) async {
    final task = _tasks[taskId];
    if (task == null) {
      logger.w('无法取消：任务不存在 - $taskId');
      return false;
    }
    
    // 更新任务状态
    task.cancel();
    _tasks[taskId] = task;
    
    // 通知负责代理
    final cancelMessage = AgentMessage(
      senderId: 'system.microkernel',
      receiverId: task.assignedTo,
      type: AgentMessageType.taskAssignment,
      content: {
        'task': task.toMap(),
        'action': 'cancel',
      },
      taskId: task.id,
    );
    
    await sendMessage(cancelMessage);
    
    // 通知协作者
    for (final collaborator in task.collaborators) {
      final collaboratorMessage = AgentMessage(
        senderId: 'system.microkernel',
        receiverId: collaborator,
        type: AgentMessageType.taskAssignment,
        content: {
          'task': task.toMap(),
          'action': 'cancel',
        },
        taskId: task.id,
      );
      
      await sendMessage(collaboratorMessage);
    }
    
    // 通知观察者
    final observers = _taskObservers[taskId] ?? [];
    for (final observer in observers) {
      try {
        observer(task);
      } catch (e) {
        logger.w('任务观察者通知失败: $e');
      }
    }
    
    logger.i('任务已取消: $taskId');
    return true;
  }
  
  @override
  String registerMessageFilter(MessageFilter filter) {
    final filterId = 'filter_${const Uuid().v4()}';
    _messageFilters[filterId] = filter;
    return filterId;
  }
  
  @override
  void unregisterMessageFilter(String filterId) {
    _messageFilters.remove(filterId);
  }
  
  @override
  List<AgentMessage> getAgentMessageHistory({
    String? agentId,
    DateTime? since,
    int? limit,
    AgentMessageType? type,
  }) {
    var messages = _messageHistory.values.toList();
    
    // 按代理ID过滤
    if (agentId != null) {
      messages = messages.where((msg) => 
          msg.senderId == agentId || msg.receiverId == agentId).toList();
    }
    
    // 按时间过滤
    if (since != null) {
      messages = messages.where((msg) => msg.timestamp.isAfter(since)).toList();
    }
    
    // 按类型过滤
    if (type != null) {
      messages = messages.where((msg) => msg.type == type).toList();
    }
    
    // 按时间排序
    messages.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    
    // 限制数量
    if (limit != null && limit > 0 && messages.length > limit) {
      messages = messages.take(limit).toList();
    }
    
    return messages;
  }
  
  @override
  List<AgentMessage> getPendingResponseMessages(String agentId) {
    return _messageHistory.values
        .where((msg) => 
            msg.receiverId == agentId && 
            msg.requiresResponse &&
            !_hasResponse(msg.id))
        .toList();
  }
  
  /// 检查消息是否有响应
  bool _hasResponse(String messageId) {
    return _messageHistory.values.any((msg) => msg.parentMessageId == messageId);
  }
  
  @override
  void clearAgentMessageHistory(String agentId, {DateTime? before}) {
    final messagesToRemove = <String>[];
    
    _messageHistory.forEach((id, msg) {
      if ((msg.senderId == agentId || msg.receiverId == agentId) &&
          (before == null || msg.timestamp.isBefore(before))) {
        messagesToRemove.add(id);
      }
    });
    
    for (final id in messagesToRemove) {
      _messageHistory.remove(id);
    }
    
    logger.i('已清理 ${messagesToRemove.length} 条消息历史记录，代理: $agentId');
  }
  
  @override
  int getActiveAgentsCount() {
    return _messageSubscribers.length;
  }
  
  @override
  void setMessageBusStrategy(MessageBusStrategy strategy) {
    _messageBusStrategy = strategy;
    logger.i('消息总线策略已设置为: $strategy');
  }
  
  /// 添加消息到历史记录
  void _addToHistory(AgentMessage message) {
    // 保持历史记录在最大大小以内
    if (_messageHistory.length >= _maxHistorySize) {
      _messageHistory.remove(_messageHistory.keys.first);
    }
    
    _messageHistory[message.id] = message;
  }
}

/// 分布式代理微内核
class DistributedAgentMicrokernel extends DefaultAgentMicrokernel {
  final String _nodeId;
  final Map<String, String> _remoteAgentNodes = {};
  
  DistributedAgentMicrokernel(
    AgentRegistry agentRegistry,
    AutonomousLearningSystem learningSystem,
    this._nodeId,
  ) : super(agentRegistry, learningSystem);
  
  /// 注册远程代理
  void registerRemoteAgent(String agentId, String nodeId) {
    _remoteAgentNodes[agentId] = nodeId;
    logger.i('远程代理已注册: $agentId 在节点 $nodeId');
  }
  
  /// 注销远程代理
  void unregisterRemoteAgent(String agentId) {
    _remoteAgentNodes.remove(agentId);
    logger.i('远程代理已注销: $agentId');
  }
  
  @override
  Future<String> sendMessage(AgentMessage message) async {
    // 检查接收者是否为远程代理
    final targetNodeId = _remoteAgentNodes[message.receiverId];
    
    if (targetNodeId != null && targetNodeId != _nodeId) {
      // 路由到远程节点
      return _routeMessageToRemoteNode(message, targetNodeId);
    }
    
    // 否则使用本地发送
    return super.sendMessage(message);
  }
  
  /// 路由消息到远程节点
  Future<String> _routeMessageToRemoteNode(
    AgentMessage message, 
    String targetNodeId,
  ) async {
    // 这里应该实现远程消息路由逻辑
    // 例如通过WebSocket、gRPC或HTTP等方式
    
    logger.i('路由消息到远程节点: $targetNodeId, 消息: ${message.id}');
    
    // 模拟消息路由成功
    return message.id;
  }
  
  /// 从远程节点接收消息
  Future<void> receiveMessageFromRemoteNode(AgentMessage message) async {
    // 验证消息
    if (message.isExpired) {
      logger.w('远程消息已过期: ${message.id}');
      return;
    }
    
    // 投递给本地代理
    await super.sendMessage(message);
  }
}

/// 代理微内核Provider
final agentMicrokernelProvider = Provider<AgentMicrokernel>((ref) {
  final agentRegistry = ref.read(agentRegistryProvider);
  final learningSystem = ref.read(autonomousLearningSystemProvider);
  return DefaultAgentMicrokernel(agentRegistry, learningSystem);
}); 