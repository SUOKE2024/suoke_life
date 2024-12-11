import 'dart:collection';
import 'message.dart';

class ConversationContext {
  final Queue<Message> _messages = Queue();
  final int maxContextLength;
  
  ConversationContext({this.maxContextLength = 10});
  
  void addUserMessage(String content) {
    _addMessage(Message(
      content: content,
      role: 'user',
      timestamp: DateTime.now(),
    ));
  }
  
  void addAssistantMessage(String content) {
    _addMessage(Message(
      content: content,
      role: 'assistant',
      timestamp: DateTime.now(),
    ));
  }
  
  void _addMessage(Message message) {
    _messages.addLast(message);
    while (_messages.length > maxContextLength) {
      _messages.removeFirst();
    }
  }
  
  List<Message> get messages => List.unmodifiable(_messages);
  
  void clear() {
    _messages.clear();
  }
  
  Map<String, dynamic> toJson() {
    return {
      'messages': messages.map((m) => m.toJson()).toList(),
      'maxContextLength': maxContextLength,
    };
  }
  
  factory ConversationContext.fromJson(Map<String, dynamic> json) {
    final context = ConversationContext(
      maxContextLength: json['maxContextLength'] as int,
    );
    
    final messagesList = json['messages'] as List;
    for (final messageJson in messagesList) {
      final message = Message.fromJson(messageJson as Map<String, dynamic>);
      context._messages.addLast(message);
    }
    
    return context;
  }
} 