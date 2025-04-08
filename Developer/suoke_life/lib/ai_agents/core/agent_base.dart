// 索克生活APP智能体基础框架
// 定义所有智能体的共同特性和接口

import 'dart:async';
import 'package:flutter/foundation.dart';
import '../config/agent_config.dart';
import '../models/agent_message.dart';
import '../models/agent_response.dart';
import '../services/model_service.dart';
import '../tools/tool_registry.dart';
import 'package:uuid/uuid.dart';
import '../core/agent_interface.dart';
import '../tools/tool_interface.dart';
import '../../core/utils/logger.dart';

/// 智能体优先级枚举
enum AgentPriority {
  critical,  // 关键优先级
  high,      // 高优先级
  medium,    // 中等优先级
  low        // 低优先级
}

/// 智能体状态枚举
enum AgentStatus {
  idle,      // 空闲状态
  busy,      // 忙碌状态
  error      // 错误状态
}

/// 基础智能体配置
class AgentConfiguration {
  final String name;         // 智能体名称
  final String version;      // 版本号
  final AgentPriority priority; // 优先级
  final List<String> capabilities; // 能力列表
  final Map<String, dynamic> metadata; // 元数据
  final String modelName;    // 使用的模型名称
  
  const AgentConfiguration({
    required this.name,
    this.version = "1.0.0",
    this.priority = AgentPriority.medium,
    this.capabilities = const [],
    this.metadata = const {},
    this.modelName = "deepseek-chat", // 默认使用DEEPSEEK模型
  });
}

/// 智能体基础类
abstract class AgentBase {
  final AgentConfiguration configuration;
  final ModelService modelService;
  final ToolRegistry toolRegistry;
  
  AgentStatus _status = AgentStatus.idle;
  final List<AgentMessage> _messageHistory = [];
  
  AgentBase({
    required this.configuration,
    required this.modelService,
    required this.toolRegistry,
  });
  
  /// 获取当前状态
  AgentStatus get status => _status;
  
  /// 获取消息历史
  List<AgentMessage> get messageHistory => List.unmodifiable(_messageHistory);
  
  /// 处理用户请求
  Future<AgentResponse> handleRequest(String userMessage, {Map<String, dynamic>? context}) async {
    if (_status == AgentStatus.busy) {
      return AgentResponse(
        text: "我正在处理其他请求，请稍候。",
        success: false,
        errorCode: "AGENT_BUSY",
      );
    }
    
    try {
      _status = AgentStatus.busy;
      
      // 记录用户消息
      _addMessage(AgentMessageType.user, userMessage);
      
      // 处理请求
      final response = await processRequest(userMessage, context: context);
      
      // 记录智能体响应
      _addMessage(AgentMessageType.agent, response.text);
      
      _status = AgentStatus.idle;
      return response;
    } catch (e) {
      _status = AgentStatus.error;
      final errorMessage = "处理请求时出错: ${e.toString()}";
      _addMessage(AgentMessageType.system, errorMessage);
      
      return AgentResponse(
        text: "抱歉，我无法完成您的请求。$errorMessage",
        success: false,
        errorCode: "PROCESSING_ERROR",
      );
    }
  }
  
  /// 清除历史记录
  void clearHistory() {
    _messageHistory.clear();
  }
  
  /// 添加消息到历史记录
  void _addMessage(AgentMessageType type, String content) {
    _messageHistory.add(AgentMessage(
      type: type,
      content: content,
      timestamp: DateTime.now(),
    ));
  }
  
  /// 由子类实现的请求处理逻辑
  @protected
  Future<AgentResponse> processRequest(String userMessage, {Map<String, dynamic>? context});
  
  /// 生成智能体系统提示词
  @protected
  String generateSystemPrompt() {
    return """
你是索克生活APP的${configuration.name}，版本${configuration.version}。
你专注于以下能力：${configuration.capabilities.join('、')}。
请始终遵循中医理论体系，注重"治未病"、"四诊合参"、"辨证施治"等核心理念。
回复时保持专业、准确、易懂，避免使用过于专业的术语，除非必要。
不要编造信息，如不确定请明确告知。
    """;
  }
  
  /// 格式化工具调用结果
  @protected
  String formatToolResult(String toolName, Map<String, dynamic> result) {
    return "工具「$toolName」执行结果：\n${result.toString()}";
  }
  
  @override
  String toString() => 'Agent(${configuration.name}, ${configuration.version})';
}

/// 基础智能体实现
abstract class BaseAgent implements Agent {
  static final Logger _logger = Logger('BaseAgent');
  static final Uuid _uuid = Uuid();
  
  /// 生成唯一ID
  static String generateId() => _uuid.v4();

  /// 智能体ID
  @override
  final String id;
  
  /// 智能体名称
  @override
  final String name;
  
  /// 智能体描述
  @override
  final String description;
  
  /// 智能体配置
  @override
  final AgentConfig config;
  
  /// 当前状态
  @override
  AgentStatus _status = AgentStatus.idle;
  
  /// 状态监听器
  final List<AgentStatusListener> _statusListeners = [];
  
  /// 工具调用监听器
  final List<ToolCallListener> _toolCallListeners = [];
  
  /// 工具调用结果监听器
  final List<ToolResultListener> _toolResultListeners = [];
  
  /// 对话历史
  final List<Message> _conversationHistory = [];
  
  /// 响应取消控制器
  StreamController<bool>? _cancelController;
  
  /// 构造函数
  BaseAgent({
    String? id,
    required this.name,
    required this.description,
    required this.config,
  }) : id = id ?? generateId();
  
  /// 获取当前状态
  @override
  AgentStatus get status => _status;
  
  /// 设置状态并通知监听器
  set status(AgentStatus newStatus) {
    if (_status != newStatus) {
      _status = newStatus;
      _notifyStatusListeners();
    }
  }
  
  /// 通知状态监听器
  void _notifyStatusListeners() {
    for (final listener in _statusListeners) {
      try {
        listener(_status);
      } catch (e, stackTrace) {
        _logger.error('状态监听器错误: $e', stackTrace);
      }
    }
  }
  
  /// 添加状态监听器
  @override
  void addStatusListener(AgentStatusListener listener) {
    _statusListeners.add(listener);
  }
  
  /// 移除状态监听器
  @override
  void removeStatusListener(AgentStatusListener listener) {
    _statusListeners.remove(listener);
  }
  
  /// 通知工具调用监听器
  void _notifyToolCallListeners(ToolCall toolCall) {
    for (final listener in _toolCallListeners) {
      try {
        listener(toolCall);
      } catch (e, stackTrace) {
        _logger.error('工具调用监听器错误: $e', stackTrace);
      }
    }
  }
  
  /// 添加工具调用监听器
  @override
  void addToolCallListener(ToolCallListener listener) {
    _toolCallListeners.add(listener);
  }
  
  /// 移除工具调用监听器
  @override
  void removeToolCallListener(ToolCallListener listener) {
    _toolCallListeners.remove(listener);
  }
  
  /// 通知工具调用结果监听器
  void _notifyToolResultListeners(String toolCallId, ToolCallResult result) {
    for (final listener in _toolResultListeners) {
      try {
        listener(toolCallId, result);
      } catch (e, stackTrace) {
        _logger.error('工具调用结果监听器错误: $e', stackTrace);
      }
    }
  }
  
  /// 添加工具调用结果监听器
  @override
  void addToolResultListener(ToolResultListener listener) {
    _toolResultListeners.add(listener);
  }
  
  /// 移除工具调用结果监听器
  @override
  void removeToolResultListener(ToolResultListener listener) {
    _toolResultListeners.remove(listener);
  }
  
  /// 添加系统提示
  @override
  void addSystemPrompt(String content) {
    addMessage(Message.system(content: content));
  }
  
  /// 添加消息到对话历史
  @override
  void addMessage(Message message) {
    _conversationHistory.add(message);
  }
  
  /// 获取对话历史
  @override
  List<Message> getConversationHistory() {
    return List.unmodifiable(_conversationHistory);
  }
  
  /// 处理用户消息
  @override
  Future<Message> processUserMessage(
    String messageContent, {
    List<String>? fileIds,
    Map<String, dynamic>? metadata,
    AgentStreamListener? onStream,
  }) async {
    try {
      // 设置状态为思考中
      status = AgentStatus.thinking;
      
      // 创建用户消息
      final userMessage = Message.user(
        content: messageContent,
        fileIds: fileIds,
        metadata: metadata,
      );
      
      // 添加到历史
      addMessage(userMessage);
      
      // 执行修剪和历史管理
      _pruneConversationHistoryIfNeeded();
      
      // 创建取消控制器
      _cancelController = StreamController<bool>();
      
      // 生成响应
      final assistantMessage = await generateResponse(
        userMessage, 
        onStream: onStream,
        cancelSignal: _cancelController!.stream,
      );
      
      // 添加助手消息到历史
      addMessage(assistantMessage);
      
      // 处理工具调用
      if (assistantMessage.toolCalls != null && 
          assistantMessage.toolCalls!.isNotEmpty) {
        // 设置状态为执行工具
        status = AgentStatus.executingTool;
        
        // 执行工具调用
        await _processToolCalls(assistantMessage.toolCalls!);
      }
      
      // 设置状态为空闲
      status = AgentStatus.idle;
      
      return assistantMessage;
    } catch (e, stackTrace) {
      // 设置状态为错误
      status = AgentStatus.error;
      
      _logger.error('处理用户消息失败: $e', stackTrace);
      
      // 添加错误消息
      final errorMessage = Message.assistant(
        content: '处理消息时出错: $e',
        metadata: {'error': e.toString()},
      );
      addMessage(errorMessage);
      
      return errorMessage;
    } finally {
      // 关闭取消控制器
      await _cancelController?.close();
      _cancelController = null;
    }
  }
  
  /// 生成响应(由子类实现)
  Future<Message> generateResponse(
    Message userMessage, {
    AgentStreamListener? onStream,
    Stream<bool>? cancelSignal,
  });
  
  /// 处理工具调用
  Future<void> _processToolCalls(List<ToolCall> toolCalls) async {
    for (final toolCall in toolCalls) {
      try {
        // 通知监听器
        _notifyToolCallListeners(toolCall);
        
        // 执行工具调用
        final result = await executeToolCall(toolCall);
        
        // 通知结果监听器
        _notifyToolResultListeners(toolCall.id, result);
        
        // 创建工具结果消息
        final toolResultMessage = Message.tool(
          content: result.output,
          toolCallId: toolCall.id,
        );
        
        // 添加到历史
        addMessage(toolResultMessage);
      } catch (e, stackTrace) {
        _logger.error('执行工具失败: ${toolCall.toolName}, $e', stackTrace);
        
        // 添加错误消息
        final errorMessage = Message.tool(
          content: '执行工具 ${toolCall.toolName} 失败: $e',
          toolCallId: toolCall.id,
          metadata: {'error': e.toString()},
        );
        
        addMessage(errorMessage);
      }
    }
  }
  
  /// 执行工具调用(由子类实现)
  @override
  Future<ToolCallResult> executeToolCall(ToolCall toolCall);
  
  /// 修剪对话历史
  void _pruneConversationHistoryIfNeeded() {
    final maxTurns = config.maxConversationTurns;
    
    if (_conversationHistory.length <= maxTurns * 2) return;
    
    // 计算要保留的轮次数
    final turnsToKeep = maxTurns;
    
    // 提取需要保留的系统消息
    final systemMessages = _conversationHistory
        .where((m) => m.type == MessageType.system)
        .toList();
    
    // 提取对话轮次(用户+助手消息对)
    final conversations = <List<Message>>[];
    
    for (int i = 0; i < _conversationHistory.length; i++) {
      if (_conversationHistory[i].type == MessageType.system) continue;
      
      if (_conversationHistory[i].type == MessageType.user) {
        final turn = <Message>[_conversationHistory[i]];
        
        // 查找用户消息之后的助手响应和工具消息
        int j = i + 1;
        while (j < _conversationHistory.length && 
               (_conversationHistory[j].type == MessageType.assistant || 
                _conversationHistory[j].type == MessageType.tool)) {
          turn.add(_conversationHistory[j]);
          j++;
        }
        
        conversations.add(turn);
        i = j - 1;
      }
    }
    
    // 保留最近的轮次
    final turnMessages = <Message>[];
    final start = conversations.length > turnsToKeep 
        ? conversations.length - turnsToKeep 
        : 0;
        
    for (int i = start; i < conversations.length; i++) {
      turnMessages.addAll(conversations[i]);
    }
    
    // 重新组织历史消息
    _conversationHistory.clear();
    _conversationHistory.addAll(systemMessages);
    _conversationHistory.addAll(turnMessages);
  }
  
  /// 清空对话历史
  @override
  Future<void> clearConversation() async {
    final systemMessages = _conversationHistory
        .where((m) => m.type == MessageType.system)
        .toList();
    
    _conversationHistory.clear();
    _conversationHistory.addAll(systemMessages);
  }
  
  /// 中断响应
  @override
  Future<void> cancelResponse() async {
    if (_cancelController != null && !_cancelController!.isClosed) {
      _cancelController!.add(true);
    }
  }
  
  /// 上传文件
  @override
  Future<String> uploadFile(List<int> fileBytes, String filename, String contentType) {
    // 默认实现为不支持
    throw UnimplementedError('此智能体不支持文件上传');
  }
  
  /// 列出文件
  @override
  Future<List<FileInfo>> listFiles() async {
    // 默认实现为不支持
    return [];
  }
  
  /// 判断是否擅长特定任务
  @override
  bool isGoodAt(String task) {
    // 默认实现，子类可覆盖
    return false;
  }
  
  /// 从另一个智能体接管对话
  @override
  Future<void> takeoverConversation(Agent otherAgent) async {
    // 复制历史消息
    final history = otherAgent.getConversationHistory();
    for (final message in history) {
      addMessage(message);
    }
    
    _logger.info('从智能体 ${otherAgent.name} 接管对话，共 ${history.length} 条消息');
  }
  
  /// 销毁智能体
  @override
  Future<void> dispose() async {
    // 清理监听器
    _statusListeners.clear();
    _toolCallListeners.clear();
    _toolResultListeners.clear();
    
    // 取消当前响应
    await cancelResponse();
  }
} 