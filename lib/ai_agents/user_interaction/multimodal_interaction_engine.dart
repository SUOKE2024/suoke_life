import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:image_picker/image_picker.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter_tts/flutter_tts.dart';

import '../../core/utils/logger.dart';
import '../models/ai_agent.dart';
import '../registry/agent_registry.dart';

/// 输入类型
enum InputType {
  /// 文本输入
  text,
  
  /// 语音输入
  voice,
  
  /// 图像输入
  image,
  
  /// 视频输入
  video,
  
  /// 文件输入
  file,
}

/// 输出类型
enum OutputType {
  /// 文本输出
  text,
  
  /// 语音输出
  voice,
  
  /// 图像输出
  image,
  
  /// 图表输出
  chart,
  
  /// 知识图谱输出
  knowledgeGraph,
}

/// 交互内容
class InteractionContent {
  /// 内容类型
  final String contentType;
  
  /// 内容数据
  final dynamic data;
  
  /// 额外元数据
  final Map<String, dynamic>? metadata;
  
  /// 构造函数
  InteractionContent({
    required this.contentType,
    required this.data,
    this.metadata,
  });
  
  /// 从Map创建
  factory InteractionContent.fromMap(Map<String, dynamic> map) {
    return InteractionContent(
      contentType: map['contentType'] as String,
      data: map['data'],
      metadata: map['metadata'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'contentType': contentType,
      'data': data,
      'metadata': metadata,
    };
  }
}

/// 用户交互
class UserInteraction {
  /// 交互ID
  final String id;
  
  /// 会话ID
  final String sessionId;
  
  /// 用户ID
  final String userId;
  
  /// 输入类型
  final InputType inputType;
  
  /// 输入内容
  final InteractionContent inputContent;
  
  /// 时间戳
  final DateTime timestamp;
  
  /// 构造函数
  UserInteraction({
    required this.id,
    required this.sessionId,
    required this.userId,
    required this.inputType,
    required this.inputContent,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
  
  /// 从Map创建
  factory UserInteraction.fromMap(Map<String, dynamic> map) {
    return UserInteraction(
      id: map['id'] as String,
      sessionId: map['sessionId'] as String,
      userId: map['userId'] as String,
      inputType: InputType.values.byName(map['inputType'] as String),
      inputContent: InteractionContent.fromMap(map['inputContent'] as Map<String, dynamic>),
      timestamp: DateTime.fromMillisecondsSinceEpoch(map['timestamp'] as int),
    );
  }
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'sessionId': sessionId,
      'userId': userId,
      'inputType': inputType.name,
      'inputContent': inputContent.toMap(),
      'timestamp': timestamp.millisecondsSinceEpoch,
    };
  }
}

/// 代理响应
class AgentResponse {
  /// 响应ID
  final String id;
  
  /// 会话ID
  final String sessionId;
  
  /// 代理ID
  final String agentId;
  
  /// 输出类型
  final OutputType outputType;
  
  /// 输出内容
  final InteractionContent outputContent;
  
  /// 时间戳
  final DateTime timestamp;
  
  /// 构造函数
  AgentResponse({
    required this.id,
    required this.sessionId,
    required this.agentId,
    required this.outputType,
    required this.outputContent,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
  
  /// 从Map创建
  factory AgentResponse.fromMap(Map<String, dynamic> map) {
    return AgentResponse(
      id: map['id'] as String,
      sessionId: map['sessionId'] as String,
      agentId: map['agentId'] as String,
      outputType: OutputType.values.byName(map['outputType'] as String),
      outputContent: InteractionContent.fromMap(map['outputContent'] as Map<String, dynamic>),
      timestamp: DateTime.fromMillisecondsSinceEpoch(map['timestamp'] as int),
    );
  }
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'sessionId': sessionId,
      'agentId': agentId,
      'outputType': outputType.name,
      'outputContent': outputContent.toMap(),
      'timestamp': timestamp.millisecondsSinceEpoch,
    };
  }
}

/// 多模态交互引擎
class MultimodalInteractionEngine {
  final AgentRegistry _agentRegistry;
  final SpeechToText _speechToText = SpeechToText();
  final FlutterTts _flutterTts = FlutterTts();
  final ImagePicker _imagePicker = ImagePicker();
  bool _speechInitialized = false;
  
  final StreamController<UserInteraction> _userInteractionController = StreamController.broadcast();
  final StreamController<AgentResponse> _agentResponseController = StreamController.broadcast();
  
  /// 用户交互流
  Stream<UserInteraction> get userInteractionStream => _userInteractionController.stream;
  
  /// 代理响应流
  Stream<AgentResponse> get agentResponseStream => _agentResponseController.stream;
  
  /// 构造函数
  MultimodalInteractionEngine(this._agentRegistry) {
    _initializeSpeech();
    _initializeTts();
  }
  
  /// 初始化语音识别
  Future<void> _initializeSpeech() async {
    try {
      _speechInitialized = await _speechToText.initialize();
    } catch (e) {
      logger.e('语音识别初始化失败', error: e);
      _speechInitialized = false;
    }
  }
  
  /// 初始化文字转语音
  Future<void> _initializeTts() async {
    try {
      await _flutterTts.setLanguage('zh-CN');
      await _flutterTts.setSpeechRate(0.5);
      await _flutterTts.setVolume(1.0);
      await _flutterTts.setPitch(1.0);
    } catch (e) {
      logger.e('文字转语音初始化失败', error: e);
    }
  }
  
  /// 处理文本输入
  Future<void> processTextInput({
    required String sessionId,
    required String userId,
    required String text,
  }) async {
    final interaction = UserInteraction(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      sessionId: sessionId,
      userId: userId,
      inputType: InputType.text,
      inputContent: InteractionContent(
        contentType: 'text/plain',
        data: text,
      ),
    );
    
    _userInteractionController.add(interaction);
    
    // 找到能处理文本输入的代理
    final agents = _agentRegistry.getAgentsByCapability(AIAgentCapability.textInput);
    if (agents.isEmpty) {
      logger.w('没有找到能处理文本输入的代理');
      return;
    }
    
    // TODO: 实现代理选择逻辑，目前简单地选择第一个代理
    final agent = agents.first;
    
    // TODO: 调用代理处理文本
    // 这里是一个简单的模拟响应
    final response = AgentResponse(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      sessionId: sessionId,
      agentId: agent.id,
      outputType: OutputType.text,
      outputContent: InteractionContent(
        contentType: 'text/plain',
        data: '您好，我是${agent.name}，我收到了您的消息: "$text"',
      ),
    );
    
    _agentResponseController.add(response);
  }
  
  /// 开始语音输入
  Future<void> startVoiceInput({
    required String sessionId,
    required String userId,
    required Function(String) onResult,
    required Function(bool) onListening,
  }) async {
    if (!_speechInitialized) {
      await _initializeSpeech();
      if (!_speechInitialized) {
        logger.e('语音识别未初始化，无法启动语音输入');
        return;
      }
    }
    
    await _speechToText.listen(
      onResult: (result) {
        final recognizedWords = result.recognizedWords;
        if (recognizedWords.isNotEmpty) {
          onResult(recognizedWords);
        }
      },
      localeId: 'zh_CN',
      listenFor: const Duration(seconds: 30),
      pauseFor: const Duration(seconds: 3),
      onSoundLevelChange: (level) {
        // 可以用来显示音量级别
      },
      cancelOnError: true,
      onDevice: true, // 尝试使用设备上的语音识别
      listenMode: ListenMode.confirmation,
    );
    
    onListening(_speechToText.isListening);
  }
  
  /// 停止语音输入
  Future<void> stopVoiceInput() async {
    await _speechToText.stop();
  }
  
  /// 处理语音输入结果
  Future<void> processVoiceResult({
    required String sessionId,
    required String userId,
    required String text,
  }) async {
    final interaction = UserInteraction(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      sessionId: sessionId,
      userId: userId,
      inputType: InputType.voice,
      inputContent: InteractionContent(
        contentType: 'text/plain',
        data: text,
        metadata: {
          'source': 'speech_to_text',
        },
      ),
    );
    
    _userInteractionController.add(interaction);
    
    // 重用文本处理逻辑
    await processTextInput(
      sessionId: sessionId,
      userId: userId,
      text: text,
    );
  }
  
  /// 处理图像输入
  Future<void> processImageInput({
    required String sessionId,
    required String userId,
    required ImageSource source,
  }) async {
    try {
      final pickedFile = await _imagePicker.pickImage(
        source: source,
        imageQuality: 80,
      );
      
      if (pickedFile == null) {
        logger.d('用户取消了图像选择');
        return;
      }
      
      final file = File(pickedFile.path);
      final bytes = await file.readAsBytes();
      final base64Image = base64Encode(bytes);
      
      final interaction = UserInteraction(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        sessionId: sessionId,
        userId: userId,
        inputType: InputType.image,
        inputContent: InteractionContent(
          contentType: 'image/jpeg',
          data: base64Image,
          metadata: {
            'filename': pickedFile.name,
            'path': pickedFile.path,
          },
        ),
      );
      
      _userInteractionController.add(interaction);
      
      // 找到能处理图像输入的代理
      final agents = _agentRegistry.getAgentsByCapability(AIAgentCapability.imageRecognition);
      if (agents.isEmpty) {
        logger.w('没有找到能处理图像输入的代理');
        return;
      }
      
      // TODO: 实现图像处理逻辑
      // 这里是一个简单的模拟响应
      final response = AgentResponse(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        sessionId: sessionId,
        agentId: agents.first.id,
        outputType: OutputType.text,
        outputContent: InteractionContent(
          contentType: 'text/plain',
          data: '我已接收到您的图片，正在分析中...',
        ),
      );
      
      _agentResponseController.add(response);
    } catch (e) {
      logger.e('处理图像输入失败', error: e);
    }
  }
  
  /// 文本转语音输出
  Future<void> speakText(String text) async {
    try {
      await _flutterTts.speak(text);
    } catch (e) {
      logger.e('文本转语音失败', error: e);
    }
  }
  
  /// 停止语音输出
  Future<void> stopSpeaking() async {
    try {
      await _flutterTts.stop();
    } catch (e) {
      logger.e('停止语音输出失败', error: e);
    }
  }
  
  /// 处理代理响应
  Future<void> processAgentResponse(AgentResponse response) async {
    _agentResponseController.add(response);
    
    // 如果用户启用了自动语音播报，将文本响应转换为语音
    if (response.outputType == OutputType.text) {
      // TODO: 检查用户偏好设置，是否启用自动语音播报
      final shouldSpeak = false; // 从用户设置中获取
      
      if (shouldSpeak) {
        await speakText(response.outputContent.data as String);
      }
    }
  }
  
  /// 释放资源
  void dispose() {
    _speechToText.cancel();
    _flutterTts.stop();
    _userInteractionController.close();
    _agentResponseController.close();
  }
} 