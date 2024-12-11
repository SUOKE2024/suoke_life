import 'dart:async';
import 'package:flutter/foundation.dart';
import '../core/network/websocket_client.dart';
import 'error_handler_service.dart';

enum MessageType {
  text,
  image,
  file,
  system
}

class ChatMessage {
  final String id;
  final String senderId;
  final String senderName;
  final MessageType type;
  final String content;
  final DateTime timestamp;
  final bool isRead;

  ChatMessage({
    required this.id,
    required this.senderId,
    required this.senderName,
    required this.type,
    required this.content,
    required this.timestamp,
    this.isRead = false,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'senderId': senderId,
      'senderName': senderName,
      'type': type.toString(),
      'content': content,
      'timestamp': timestamp.toIso8601String(),
      'isRead': isRead,
    };
  }

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'],
      senderId: json['senderId'],
      senderName: json['senderName'],
      type: MessageType.values.firstWhere(
        (e) => e.toString() == json['type'],
        orElse: () => MessageType.text,
      ),
      content: json['content'],
      timestamp: DateTime.parse(json['timestamp']),
      isRead: json['isRead'] ?? false,
    );
  }
}

class ConferenceChatService {
  final WebSocketClient _wsClient;
  final ErrorHandlerService _errorHandler;
  final String _userId;
  final String _userName;
  
  final _messageController = StreamController<ChatMessage>.broadcast();
  final _typingController = StreamController<Map<String, bool>>.broadcast();
  
  final Map<String, bool> _typingUsers = {};
  Timer? _typingTimer;

  ConferenceChatService({
    required WebSocketClient wsClient,
    required ErrorHandlerService errorHandler,
    required String userId,
    required String userName,
  }) : _wsClient = wsClient,
       _errorHandler = errorHandler,
       _userId = userId,
       _userName = userName {
    _initializeMessageHandling();
  }

  void _initializeMessageHandling() {
    _wsClient.messages.listen(
      (message) {
        try {
          if (message is Map<String, dynamic>) {
            if (message['type'] == 'chat') {
              final chatMessage = ChatMessage.fromJson(message['data']);
              _messageController.add(chatMessage);
            } else if (message['type'] == 'typing') {
              final userId = message['userId'];
              final isTyping = message['isTyping'];
              _updateTypingStatus(userId, isTyping);
            }
          }
        } catch (e, stackTrace) {
          _errorHandler.handleError(
            'CHAT_MESSAGE_PARSE_ERROR',
            '解析聊天消息失败: ${e.toString()}',
            ErrorSeverity.low,
            originalError: e,
            stackTrace: stackTrace,
          );
        }
      },
      onError: (error, stackTrace) {
        _errorHandler.handleError(
          'CHAT_WEBSOCKET_ERROR',
          '聊天连接错误: ${error.toString()}',
          ErrorSeverity.medium,
          originalError: error,
          stackTrace: stackTrace,
        );
      },
    );
  }

  Future<void> sendMessage(String content, {MessageType type = MessageType.text}) async {
    try {
      final message = ChatMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        senderId: _userId,
        senderName: _userName,
        type: type,
        content: content,
        timestamp: DateTime.now(),
      );

      await _wsClient.send({
        'type': 'chat',
        'data': message.toJson(),
      });

      // 本地立即显示消息
      _messageController.add(message);
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'CHAT_SEND_ERROR',
        '发送消息失败: ${e.toString()}',
        ErrorSeverity.medium,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  void sendTypingStatus(bool isTyping) {
    _typingTimer?.cancel();

    try {
      _wsClient.send({
        'type': 'typing',
        'userId': _userId,
        'isTyping': isTyping,
      });

      if (isTyping) {
        // 5秒后自动设置为不在输入状态
        _typingTimer = Timer(const Duration(seconds: 5), () {
          sendTypingStatus(false);
        });
      }
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'CHAT_TYPING_ERROR',
        '发送输入状态失败: ${e.toString()}',
        ErrorSeverity.low,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  void _updateTypingStatus(String userId, bool isTyping) {
    _typingUsers[userId] = isTyping;
    _typingController.add(Map.from(_typingUsers));
  }

  Future<void> markMessageAsRead(String messageId) async {
    try {
      await _wsClient.send({
        'type': 'messageRead',
        'messageId': messageId,
        'userId': _userId,
      });
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'CHAT_MARK_READ_ERROR',
        '标记消息已读失败: ${e.toString()}',
        ErrorSeverity.low,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  // Getters
  Stream<ChatMessage> get messages => _messageController.stream;
  Stream<Map<String, bool>> get typingUsers => _typingController.stream;

  void dispose() {
    _messageController.close();
    _typingController.close();
    _typingTimer?.cancel();
  }
} 