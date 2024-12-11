/// Repository that handles chat data operations.
/// 
/// Features:
/// - Message persistence
/// - Chat history management
/// - Data synchronization
class ChatRepositoryImpl implements ChatRepository {
  final NetworkService _network;
  final StorageService _storage;

  ChatRepositoryImpl(this._network, this._storage);

  @override
  Future<List<ChatMessage>> getMessages(String chatId) async {
    try {
      // Try loading from cache first
      final cached = await _loadFromCache(chatId);
      if (cached != null) {
        return cached;
      }

      // Fetch from network
      final response = await _network.get('/api/chats/$chatId/messages');
      final messages = (response.data as List)
          .map((json) => ChatMessage.fromJson(json))
          .toList();

      // Cache the results
      await _saveToCache(chatId, messages);

      return messages;
    } catch (e) {
      LoggerService.error('Failed to get messages', error: e);
      rethrow;
    }
  }

  @override
  Future<ChatMessage> sendMessage(ChatMessage message) async {
    try {
      final response = await _network.post(
        '/api/messages',
        body: message.toJson(),
      );
      
      final sentMessage = ChatMessage.fromJson(response.data);
      
      // Update cache
      await _addMessageToCache(message.chatId, sentMessage);

      return sentMessage;
    } catch (e) {
      LoggerService.error('Failed to send message', error: e);
      rethrow;
    }
  }

  @override
  Future<void> deleteMessage(String messageId) async {
    try {
      await _network.delete('/api/messages/$messageId');
      
      // Update cache
      await _removeMessageFromCache(messageId);
    } catch (e) {
      LoggerService.error('Failed to delete message', error: e);
      rethrow;
    }
  }

  @override
  Future<List<Chat>> getChats() async {
    try {
      final response = await _network.get('/api/chats');
      return (response.data as List)
          .map((json) => Chat.fromJson(json))
          .toList();
    } catch (e) {
      LoggerService.error('Failed to get chats', error: e);
      rethrow;
    }
  }

  Future<List<ChatMessage>?> _loadFromCache(String chatId) async {
    final cached = await _storage.getObject<List<dynamic>>(
      'chat_messages_$chatId',
      (json) => json
          .map((e) => ChatMessage.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
    return cached;
  }

  Future<void> _saveToCache(String chatId, List<ChatMessage> messages) async {
    await _storage.setObject(
      'chat_messages_$chatId',
      messages.map((m) => m.toJson()).toList(),
    );
  }

  Future<void> _addMessageToCache(String chatId, ChatMessage message) async {
    final messages = await _loadFromCache(chatId) ?? [];
    messages.add(message);
    await _saveToCache(chatId, messages);
  }

  Future<void> _removeMessageFromCache(String messageId) async {
    // Implement cache cleanup
  }
}

/// Chat model representing a conversation
class Chat {
  final String id;
  final String name;
  final List<String> participants;
  final DateTime lastMessageAt;
  final ChatMessage? lastMessage;

  Chat({
    required this.id,
    required this.name,
    required this.participants,
    required this.lastMessageAt,
    this.lastMessage,
  });

  factory Chat.fromJson(Map<String, dynamic> json) => Chat(
    id: json['id'] as String,
    name: json['name'] as String,
    participants: (json['participants'] as List)
        .map((e) => e as String)
        .toList(),
    lastMessageAt: DateTime.parse(json['last_message_at'] as String),
    lastMessage: json['last_message'] != null
        ? ChatMessage.fromJson(json['last_message'])
        : null,
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'participants': participants,
    'last_message_at': lastMessageAt.toIso8601String(),
    'last_message': lastMessage?.toJson(),
  };
} 