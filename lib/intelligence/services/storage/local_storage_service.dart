class LocalStorageService implements DataStorageService {
  final Box<Map> _messageBox;
  
  LocalStorageService(this._messageBox);
  
  static Future<LocalStorageService> initialize() async {
    final box = await Hive.openBox<Map>('chat_messages');
    return LocalStorageService(box);
  }

  @override
  Future<void> saveMessage(ChatMessage message) async {
    final key = _getKey(message.userId!, message.assistantName!);
    final messages = await getMessages(
      userId: message.userId!,
      assistantName: message.assistantName!,
    );
    
    messages.add(message);
    await _messageBox.put(key, {
      'messages': messages.map((m) => m.toMap()).toList(),
    });
  }

  @override
  Future<List<ChatMessage>> getMessages({
    required String userId,
    required String assistantName,
    int limit = 20,
  }) async {
    final key = _getKey(userId, assistantName);
    final data = _messageBox.get(key);
    
    if (data == null) return [];
    
    final messages = (data['messages'] as List)
      .map((m) => ChatMessage.fromMap(Map<String, dynamic>.from(m)))
      .toList();
    
    return messages.length > limit ? 
      messages.sublist(messages.length - limit) : 
      messages;
  }

  @override
  Future<void> clearMessages({
    required String userId,
    required String assistantName,
  }) async {
    final key = _getKey(userId, assistantName);
    await _messageBox.delete(key);
  }

  String _getKey(String userId, String assistantName) => 
    'chat_${userId}_${assistantName}';
} 