/// Controller that manages chat detail page state and interactions.
/// 
/// Features:
/// - Message loading
/// - Message sending
/// - Attachment handling
/// - Typing indicators
class ChatDetailController extends BaseController {
  final ChatService _chatService;
  final MessageService _messageService;

  final _messages = <ChatMessage>[].obs;
  final _attachments = <Attachment>[].obs;
  final _typingUsers = <String>[].obs;
  final _isLoading = false.obs;
  final _hasMore = true.obs;

  String get chatId => Get.parameters['chatId'] ?? '';
  List<ChatMessage> get messages => _messages;
  List<Attachment> get attachments => _attachments;
  List<String> get typingUsers => _typingUsers;
  bool get isLoading => _isLoading.value;
  bool get hasMore => _hasMore.value;

  late final ScrollController scrollController;
  late final TextEditingController messageController;
  late final StreamSubscription _messageSubscription;
  late final StreamSubscription _typingSubscription;

  ChatDetailController(this._chatService, this._messageService);

  @override
  void onInit() {
    super.onInit();
    scrollController = ScrollController()..addListener(_onScroll);
    messageController = TextEditingController();
    _setupSubscriptions();
    _loadInitialMessages();
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

  Future<void> _loadInitialMessages() async {
    await runAsync(() async {
      final messages = await _chatService.getChatMessages(chatId);
      _messages.value = messages;
      _scrollToBottom();
    });
  }

  Future<void> _loadMoreMessages() async {
    if (!_hasMore.value || _isLoading.value) return;

    await runAsync(() async {
      _isLoading.value = true;
      final oldestMessageId = _messages.first.id;
      final moreMessages = await _chatService.getMessagesBefore(
        chatId,
        oldestMessageId,
      );
      if (moreMessages.isEmpty) {
        _hasMore.value = false;
      } else {
        _messages.insertAll(0, moreMessages);
      }
    });
  }

  Future<void> sendMessage() async {
    final content = messageController.text.trim();
    if (content.isEmpty && attachments.isEmpty) return;

    try {
      // Format message content
      final formattedContent = await _messageService.formatMessage(content);
      
      // Validate message
      await _messageService.validateMessage(formattedContent);

      // Send message
      await _chatService.sendMessage(
        chatId,
        formattedContent,
        attachments: _attachments,
      );

      // Clear input
      messageController.clear();
      _attachments.clear();
      
      // Scroll to bottom
      _scrollToBottom();
    } catch (e) {
      showError('Failed to send message');
    }
  }

  Future<void> addAttachment() async {
    try {
      final files = await FilePicker.platform.pickFiles(
        type: FileType.any,
        allowMultiple: true,
      );

      if (files != null) {
        final fileList = files.paths
            .map((path) => File(path!))
            .toList();

        final processedAttachments = await _messageService.processAttachments(
          fileList,
        );
        _attachments.addAll(processedAttachments);
      }
    } catch (e) {
      showError('Failed to add attachment');
    }
  }

  void removeAttachment(String attachmentId) {
    _attachments.removeWhere((a) => a.id == attachmentId);
  }

  void startTyping() {
    _chatService.setTyping(chatId, true);
  }

  void stopTyping() {
    _chatService.setTyping(chatId, false);
  }

  void _handleNewMessage(ChatMessage message) {
    _messages.add(message);
    _scrollToBottom();
  }

  void _handleTypingEvent(TypingEvent event) {
    if (event.isTyping) {
      if (!_typingUsers.contains(event.userId)) {
        _typingUsers.add(event.userId);
      }
    } else {
      _typingUsers.remove(event.userId);
    }
  }

  void _onScroll() {
    if (scrollController.position.pixels == 
        scrollController.position.maxScrollExtent) {
      _loadMoreMessages();
    }
  }

  void _scrollToBottom() {
    if (scrollController.hasClients) {
      scrollController.animateTo(
        scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  @override
  void onClose() {
    scrollController.dispose();
    messageController.dispose();
    _messageSubscription.cancel();
    _typingSubscription.cancel();
    stopTyping();
    super.onClose();
  }
} 