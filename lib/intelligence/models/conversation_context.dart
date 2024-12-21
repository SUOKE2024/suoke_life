import 'dart:collection';
import 'message.dart';

class ConversationContext {
  final Map<String, dynamic> _data = {};
  final List<ChatMessage> _history = [];
  final int _maxHistory;
  
  ConversationContext({int? maxHistory}) : _maxHistory = maxHistory ?? 10;

  void update(Map<String, dynamic> updates) {
    _data.addAll(updates);
    _data['last_update'] = DateTime.now().toIso8601String();
  }

  void addMessage(ChatMessage message) {
    _history.add(message);
    if (_history.length > _maxHistory) {
      _history.removeAt(0);
    }
    _data['last_message_time'] = message.timestamp.toIso8601String();
  }

  List<ChatMessage> getHistory([int? limit]) {
    if (limit == null || limit >= _history.length) {
      return List.unmodifiable(_history);
    }
    return List.unmodifiable(_history.skip(_history.length - limit));
  }

  Map<String, dynamic> toMap() {
    return {
      'data': Map<String, dynamic>.from(_data),
      'history': _history.map((m) => m.toMap()).toList(),
      'max_history': _maxHistory,
      'last_update': DateTime.now().toIso8601String(),
    };
  }

  factory ConversationContext.fromMap(Map<String, dynamic> map) {
    final context = ConversationContext(
      maxHistory: map['max_history'] as int,
    );
    
    context._data.addAll(Map<String, dynamic>.from(map['data']));
    
    final historyList = map['history'] as List;
    for (final messageMap in historyList) {
      context._history.add(
        ChatMessage.fromMap(Map<String, dynamic>.from(messageMap))
      );
    }
    
    return context;
  }

  void clear() {
    _data.clear();
    _history.clear();
  }

  bool get isEmpty => _data.isEmpty && _history.isEmpty;
  
  DateTime? get lastUpdate => 
    _data['last_update'] != null ? 
    DateTime.parse(_data['last_update']) : null;
} 