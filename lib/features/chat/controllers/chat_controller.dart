/// Controller that manages chat UI state and user interactions.
class ChatController extends BaseController {
  final ChatService _chatService;
  final _messages = <ChatMessage>[].obs;
  final _isTyping = false.obs;
  
  late final StreamSubscription _messageSubscription;
  late final StreamSubscription _typingSubscription;
  
  String get chatId => Get.parameters['chatId'] ?? '';

  ChatController(this._chatService);

  @override
  void onInit() {
    super.onInit();
    _loadMessages();
    _setupSubscriptions();
  }

  void _loadMessages() {
    _messages.value = _chatService.getChatMessages(chatId);
  }

  void _setupSubscriptions() {
    // Listen for new messages
    _messageSubscription = _chatService.messageStream
        .where((message) => message.chatId == chatId)
        .listen(_handleNewMessage);

    // Listen for typing events  
    _typingSubscription = _chatService.typingStream
        .where((event) => event.chatId == chatId)
        .listen(_handleTypingEvent);
  }

  Future<void> sendMessage(String content) async {
    if (content.trim().isEmpty) return;

    try {
      await runAsync(() async {
        await _chatService.sendMessage(chatId, content);
      });
    } catch (e) {
      showError('Failed to send message');
    }
  }

  void startTyping() {
    if (!_isTyping.value) {
      _isTyping.value = true;
      _chatService.setTyping(chatId, true);
    }
  }

  void stopTyping() {
    if (_isTyping.value) {
      _isTyping.value = false;
      _chatService.setTyping(chatId, false);
    }
  }

  void _handleNewMessage(ChatMessage message) {
    _messages.add(message);
  }

  void _handleTypingEvent(TypingEvent event) {
    // Handle typing indicator
  }

  @override
  void onClose() {
    _messageSubscription.cancel();
    _typingSubscription.cancel();
    stopTyping();
    super.onClose();
  }
} 