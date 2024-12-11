import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/message.dart';
import 'coze_service.dart';
import 'claude_service.dart';
import 'message_storage_service.dart';

class AIService extends GetxController {
  final List<Message> _messages = [];
  final Map<String, dynamic> _context = {};
  final _cozeService = CozeService(
    botId: 'your_coze_bot_id',
    token: 'your_coze_token',
  );
  final _claudeService = ClaudeService(
    sessionId: DateTime.now().toString(),
  );
  final _storageService = MessageStorageService();
  
  String _currentAssistant = 'soer';
  bool _isProcessing = false;
  Timer? _autoSaveTimer;

  List<Message> get messages => List.unmodifiable(_messages);
  bool get isProcessing => _isProcessing;
  String get currentAssistant => _currentAssistant;

  AIService() {
    _setupAutoSave();
    loadMessages();
  }

  void _setupAutoSave() {
    _autoSaveTimer?.cancel();
    _autoSaveTimer = Timer.periodic(
      const Duration(minutes: 1),
      (_) => saveMessages(),
    );
  }

  @override
  void dispose() {
    _autoSaveTimer?.cancel();
    saveMessages();
    super.dispose();
  }
  
  void setAssistant(String assistant) {
    if (_currentAssistant == assistant) return;
    
    saveMessages(); // 保存当前助手的消息
    _currentAssistant = assistant;
    loadMessages(); // 加载新助手的消息
    update();
  }

  Future<void> sendMessage(String content, String role) async {
    if (content.trim().isEmpty) return;

    final userMessage = Message(
      content: content,
      role: role,
    );
    
    _messages.add(userMessage);
    update();
    await saveMessages();

    if (role == 'user') {
      _isProcessing = true;
      update();

      try {
        final response = await _getAssistantResponse(content);
        final assistantMessage = Message(
          content: response,
          role: _currentAssistant,
          metadata: {
            'context': _context,
          },
        );
        
        _messages.add(assistantMessage);
        await saveMessages();
      } catch (e) {
        final errorMessage = Message(
          content: '抱歉，我现在无法回答您的问题。请稍后再试。',
          role: _currentAssistant,
          metadata: {
            'error': e.toString(),
          },
        );
        
        _messages.add(errorMessage);
        await saveMessages();
      } finally {
        _isProcessing = false;
        update();
      }
    }
  }

  Future<String> _getAssistantResponse(String userMessage) async {
    switch (_currentAssistant) {
      case 'soer':
        return await _cozeService.sendMessage(userMessage);
      case 'claude':
        return await _claudeService.sendMessage(userMessage);
      default:
        throw Exception('Unknown assistant type: $_currentAssistant');
    }
  }

  Future<void> clearMessages() async {
    _messages.clear();
    _context.clear();
    await _storageService.clearMessages(_currentAssistant);
    update();
  }

  void updateContext(Map<String, dynamic> newContext) {
    _context.addAll(newContext);
  }

  Future<void> loadMessages() async {
    try {
      final savedMessages = await _storageService.loadMessages(_currentAssistant);
      _messages.clear();
      _messages.addAll(savedMessages);
      update();
    } catch (e) {
      print('Error loading messages: $e');
    }
  }

  Future<void> saveMessages() async {
    try {
      await _storageService.saveMessages(_currentAssistant, _messages);
    } catch (e) {
      print('Error saving messages: $e');
    }
  }

  Future<Map<String, int>> getMessageStats() async {
    return await _storageService.getMessageStats();
  }

  Future<void> deleteAllMessages() async {
    await _storageService.deleteAllMessages();
    _messages.clear();
    update();
  }
} 