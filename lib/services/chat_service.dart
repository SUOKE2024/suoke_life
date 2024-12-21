import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../models/chat_message.dart';
import 'doubao_api_service.dart';
import 'biometric_analysis_service.dart';
import 'voice_service.dart';
import 'video_service.dart';
import '../data/local/database/app_database.dart';
import 'ai_service.dart';

class ChatService extends GetxController {
  final DoubaoApiService _apiService;
  final BiometricAnalysisService _biometricService;
  final VoiceService _voiceService;
  final VideoService _videoService;
  final AppDatabase _localDb;
  final AIService _aiService;
  
  final List<ChatMessage> _messages = [];
  bool _isLoading = false;
  bool _isAnalyzing = false;
  
  final _messageController = StreamController<ChatMessage>.broadcast();
  final _biometricController = StreamController<BiometricAnalysisResult>.broadcast();
  
  ChatService({
    DoubaoApiService? apiService,
    BiometricAnalysisService? biometricService,
    VoiceService? voiceService,
    VideoService? videoService,
    AppDatabase? localDb,
    AIService? aiService,
  }) : _apiService = apiService ?? DoubaoApiService(),
       _biometricService = biometricService ?? BiometricAnalysisService(
         httpClient: HttpClient(),
         wsClient: WebSocketClient(),
         dataCollectionService: RealtimeDataCollectionService(),
       ),
       _voiceService = voiceService ?? VoiceService(),
       _videoService = videoService ?? VideoService(),
       _localDb = localDb ?? AppDatabase(),
       _aiService = aiService ?? AIService(_localDb) {
    _initializeServices();
  }

  void _initializeServices() {
    // 监听生物特征分析结果
    _biometricService.analysisStream.listen((result) {
      _biometricController.add(result);
      _enrichMessageWithBiometricData(result);
    });

    // 监听语音服务
    _voiceService.audioStream.listen((audioData) {
      if (_isAnalyzing) {
        _biometricService.analyzeVoiceData(BiometricData(
          type: BiometricType.voice,
          data: audioData,
          timestamp: DateTime.now(),
        ));
      }
    });

    // 监听视频服务
    _videoService.videoStream.listen((videoFrame) {
      if (_isAnalyzing) {
        _biometricService.analyzeFaceData(BiometricData(
          type: BiometricType.face,
          data: videoFrame,
          timestamp: DateTime.now(),
        ));
      }
    });
  }

  void _enrichMessageWithBiometricData(BiometricAnalysisResult result) {
    if (_messages.isEmpty) return;
    
    final lastMessage = _messages.last;
    if (lastMessage.role == MessageRole.user) {
      final enrichedMessage = ChatMessage.user(
        content: lastMessage.content,
        metadata: {
          ...lastMessage.metadata ?? {},
          'biometric_${result.type}': result.toJson(),
        },
      );
      
      // 更新消���
      _messages[_messages.length - 1] = enrichedMessage;
      _messageController.add(enrichedMessage);
      update();
    }
  }

  // 获取所有消息
  List<ChatMessage> get messages => List.unmodifiable(_messages);
  
  // 获取加载状态
  bool get isLoading => _isLoading;
  
  // 获取消息流
  Stream<ChatMessage> get messageStream => _messageController.stream;
  
  // 获取生物特征分析结果流
  Stream<BiometricAnalysisResult> get biometricStream => _biometricController.stream;

  // 开始分析
  void startAnalysis() {
    if (_isAnalyzing) return;
    _isAnalyzing = true;
    _biometricService.startAnalysis();
    _voiceService.startRecording();
    _videoService.startCapture();
  }

  // 停止分析
  void stopAnalysis() {
    if (!_isAnalyzing) return;
    _isAnalyzing = false;
    _biometricService.stopAnalysis();
    _voiceService.stopRecording();
    _videoService.stopCapture();
  }

  // 发送消息
  Future<void> sendMessage(String content, {bool withBiometric = true}) async {
    if (content.trim().isEmpty) return;

    if (withBiometric) {
      startAnalysis();
    }

    // 创建用户消息
    final userMessage = ChatMessage.user(content: content);
    _addMessage(userMessage);

    try {
      _isLoading = true;
      update();

      final messages = _messages
          .map((msg) => {
                'role': msg.role.toString().split('.').last,
                'content': msg.content,
                'biometric_data': msg.metadata?['biometric_data'],
              })
          .toList();

      final response = await _apiService.sendMessage(messages);
      
      if (response['success'] == true && response['data'] != null) {
        final aiMessage = ChatMessage.assistant(
          content: response['data']['choices'][0]['message']['content'],
          metadata: {
            'usage': response['data']['usage'],
            'model': response['data']['model'],
          },
        );
        _addMessage(aiMessage);
      } else {
        final errorMessage = ChatMessage.error(
          content: response['message'] ?? '发送消息失败',
          metadata: {'error': response['error']},
        );
        _addMessage(errorMessage);
      }
    } catch (e) {
      final errorMessage = ChatMessage.error(
        content: '发送消息时发生错误',
        metadata: {'error': e.toString()},
      );
      _addMessage(errorMessage);
    } finally {
      _isLoading = false;
      if (withBiometric) {
        // 延迟停止分析，确保捕获完整的生物特征数据
        Future.delayed(Duration(seconds: 2), stopAnalysis);
      }
      update();
    }
  }

  void _addMessage(ChatMessage message) {
    _messages.add(message);
    _messageController.add(message);
    update();
  }

  void clearMessages() {
    _messages.clear();
    update();
  }

  @override
  void dispose() {
    stopAnalysis();
    _messageController.close();
    _biometricController.close();
    super.dispose();
  }

  // 发送消息
  Future<void> sendMessage(Map<String, dynamic> message) async {
    final db = await _localDb.database;
    
    // 存储消息
    await db.insert('chat_messages', {
      'id': DateTime.now().millisecondsSinceEpoch.toString(),
      'content': message['content'],
      'type': message['type'],
      'timestamp': DateTime.now().millisecondsSinceEpoch,
    });

    // 如果是多模态内容，进行处理
    if (message['content_type'] != 'text') {
      await _aiService.processMultiModalContent(
        message['content'],
        message['content_type'],
        message['metadata'] ?? {},
      );
    }
  }

  // 获取聊天历史
  Future<List<Map<String, dynamic>>> getChatHistory(String chatType) async {
    final db = await _localDb.database;
    return await db.query(
      'chat_messages',
      where: 'type = ?',
      whereArgs: [chatType],
      orderBy: 'timestamp DESC',
    );
  }
} 