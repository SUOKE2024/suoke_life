/// Controller that manages chat list page state and interactions.
/// 
/// Features:
/// - Chat list loading
/// - Chat searching
/// - Chat filtering
class ChatListController extends BaseController {
  final ChatService _chatService;
  
  final _chats = <Chat>[].obs;
  final _filteredChats = <Chat>[].obs;
  final _searchQuery = ''.obs;
  final _selectedFilter = ChatFilter.all.obs;

  List<Chat> get chats => _filteredChats;
  String get searchQuery => _searchQuery.value;
  ChatFilter get selectedFilter => _selectedFilter.value;

  ChatListController(this._chatService);

  @override
  void onInit() {
    super.onInit();
    _loadChats();
    ever(_searchQuery, (_) => _filterChats());
    ever(_selectedFilter, (_) => _filterChats());
  }

  Future<void> _loadChats() async {
    await runAsync(() async {
      final chats = await _chatService.getChats();
      _chats.value = chats;
      _filterChats();
    });
  }

  void setSearchQuery(String query) {
    _searchQuery.value = query;
  }

  void setFilter(ChatFilter filter) {
    _selectedFilter.value = filter;
  }

  void _filterChats() {
    var filtered = _chats.toList();

    // Apply search
    if (searchQuery.isNotEmpty) {
      filtered = filtered.where((chat) {
        return chat.name.toLowerCase().contains(searchQuery.toLowerCase());
      }).toList();
    }

    // Apply filter
    switch (selectedFilter) {
      case ChatFilter.all:
        break;
      case ChatFilter.unread:
        filtered = filtered.where((chat) => chat.unreadCount > 0).toList();
        break;
      case ChatFilter.active:
        filtered = filtered.where((chat) => chat.isActive).toList();
        break;
      case ChatFilter.archived:
        filtered = filtered.where((chat) => chat.isArchived).toList();
        break;
    }

    _filteredChats.value = filtered;
  }

  Future<void> refreshChats() async {
    await _loadChats();
  }

  Future<void> archiveChat(String chatId) async {
    await runAsync(() async {
      await _chatService.archiveChat(chatId);
      await refreshChats();
    });
  }

  Future<void> deleteChat(String chatId) async {
    await runAsync(() async {
      await _chatService.deleteChat(chatId);
      await refreshChats();
    });
  }
}

/// Chat list filter options
enum ChatFilter {
  all,
  unread,
  active,
  archived,
} 