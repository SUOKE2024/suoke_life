/// Service that handles chat functionality and message management.
/// 
/// Features:
/// - Message sending/receiving
/// - Chat history management
/// - Real-time updates
class ChatService extends BaseService {
  final int maxMessageCount;
  final bool enableVoice;
  
  final _messages = <String, List<ChatMessage>>{}.obs;
  final _activeChats = <String>{}.obs;
  final _typing = <String, bool>{}.obs;

  final _messageController = StreamController<ChatMessage>.broadcast();
  final _typingController = StreamController<TypingEvent>.broadcast();

  ChatService({
    this.maxMessageCount = 100,
    this.enableVoice = true,
  });

  @override
  List<Type> get dependencies => [
    StorageService,
    NetworkService,
    AnalyticsService,
  ];

  @override
  Future<void> initialize() async {
    // Load chat history
    await _loadChatHistory();
    
    // Initialize real-time connection
    await _initializeRealtime();
    
    // Setup message cleanup
    _setupMessageCleanup();
  }

  Future<void> _loadChatHistory() async {
    final storage = DependencyManager.instance.get<StorageService>();
    final history = await storage.getObject<Map<String, List<ChatMessage>>>(
      'chat_history',
      (json) => _deserializeChatHistory(json),
    );
    if (history != null) {
      _messages.value = history;
    }
  }

  Future<void> _initializeRealtime() async {
    final network = DependencyManager.instance.get<NetworkService>();
    await network.connectWebSocket(
      onMessage: _handleIncomingMessage,
      onTyping: _handleTypingEvent,
    );
  }

  void _setupMessageCleanup() {
    // Cleanup old messages periodically
    Timer.periodic(const Duration(hours: 1), (_) {
      _cleanupOldMessages();
    });
  }

  Future<void> sendMessage(String chatId, String content) async {
    try {
      // Create message
      final message = ChatMessage(
        id: const Uuid().v4(),
        chatId: chatId,
        content: content,
        senderId: getCurrentUserId(),
        timestamp: DateTime.now(),
      );

      // Save locally
      _addMessage(chatId, message);

      // Send to server
      await _sendToServer(message);

      // Track analytics
      _trackMessageSent(message);
    } catch (e) {
      LoggerService.error('Failed to send message', error: e);
      rethrow;
    }
  }

  void setTyping(String chatId, bool isTyping) {
    _typing[chatId] = isTyping;
    _typingController.add(TypingEvent(
      chatId: chatId,
      userId: getCurrentUserId(),
      isTyping: isTyping,
    ));
  }

  Stream<ChatMessage> get messageStream => _messageController.stream;
  Stream<TypingEvent> get typingStream => _typingController.stream;

  List<ChatMessage> getChatMessages(String chatId) {
    return _messages[chatId] ?? [];
  }

  bool isUserTyping(String chatId, String userId) {
    return _typing[chatId] == true;
  }

  void _addMessage(String chatId, ChatMessage message) {
    final messages = _messages[chatId] ?? [];
    messages.add(message);
    _messages[chatId] = messages;
    _messageController.add(message);
  }

  Future<void> _sendToServer(ChatMessage message) async {
    final network = DependencyManager.instance.get<NetworkService>();
    await network.post(
      '/api/messages',
      body: message.toJson(),
    );
  }

  void _handleIncomingMessage(Map<String, dynamic> data) {
    final message = ChatMessage.fromJson(data);
    _addMessage(message.chatId, message);
  }

  void _handleTypingEvent(Map<String, dynamic> data) {
    final event = TypingEvent.fromJson(data);
    _typing[event.chatId] = event.isTyping;
    _typingController.add(event);
  }

  void _cleanupOldMessages() {
    for (final chatId in _messages.keys) {
      final messages = _messages[chatId] ?? [];
      if (messages.length > maxMessageCount) {
        _messages[chatId] = messages.sublist(
          messages.length - maxMessageCount,
        );
      }
    }
  }

  void _trackMessageSent(ChatMessage message) {
    final analytics = DependencyManager.instance.get<AnalyticsService>();
    analytics.trackEvent(
      'message_sent',
      parameters: {
        'chat_id': message.chatId,
        'message_length': message.content.length,
        'has_attachments': message.attachments?.isNotEmpty ?? false,
      },
    );
  }

  String getCurrentUserId() {
    final auth = DependencyManager.instance.get<AuthService>();
    return auth.currentUser?.id ?? '';
  }

  @override
  Future<void> dispose() async {
    await _messageController.close();
    await _typingController.close();
  }

  Map<String, List<ChatMessage>> _deserializeChatHistory(
    Map<String, dynamic> json,
  ) {
    final history = <String, List<ChatMessage>>{};
    json.forEach((key, value) {
      history[key] = (value as List)
          .map((e) => ChatMessage.fromJson(e))
          .toList();
    });
    return history;
  }
}

/// Chat message model
class ChatMessage {
  final String id;
  final String chatId;
  final String content;
  final String senderId;
  final DateTime timestamp;
  final List<Attachment>? attachments;

  ChatMessage({
    required this.id,
    required this.chatId,
    required this.content,
    required this.senderId,
    required this.timestamp,
    this.attachments,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) => ChatMessage(
    id: json['id'] as String,
    chatId: json['chat_id'] as String,
    content: json['content'] as String,
    senderId: json['sender_id'] as String,
    timestamp: DateTime.parse(json['timestamp'] as String),
    attachments: (json['attachments'] as List?)
        ?.map((e) => Attachment.fromJson(e))
        .toList(),
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'chat_id': chatId,
    'content': content,
    'sender_id': senderId,
    'timestamp': timestamp.toIso8601String(),
    'attachments': attachments?.map((e) => e.toJson()).toList(),
  };
}

/// Typing event model
class TypingEvent {
  final String chatId;
  final String userId;
  final bool isTyping;

  TypingEvent({
    required this.chatId,
    required this.userId,
    required this.isTyping,
  });

  factory TypingEvent.fromJson(Map<String, dynamic> json) => TypingEvent(
    chatId: json['chat_id'] as String,
    userId: json['user_id'] as String,
    isTyping: json['is_typing'] as bool,
  );

  Map<String, dynamic> toJson() => {
    'chat_id': chatId,
    'user_id': userId,
    'is_typing': isTyping,
  };
} 