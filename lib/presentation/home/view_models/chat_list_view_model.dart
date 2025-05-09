import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/models/chat_contact_model.dart';
import 'package:suoke_life/domain/repositories/chat_repository.dart';

/// 聊天列表视图模型状态
class ChatListViewState {
  /// 是否正在加载
  final bool isLoading;
  
  /// 错误信息
  final String? errorMessage;
  
  /// 所有聊天联系人
  final List<ChatContact> allContacts;
  
  /// 收藏的联系人
  final List<ChatContact> favoriteContacts;
  
  /// 智能体联系人
  final List<ChatContact> agentContacts;
  
  /// 名医联系人
  final List<ChatContact> doctorContacts;
  
  /// 供应商联系人
  final List<ChatContact> providerContacts;
  
  /// 最近联系人
  final List<ChatContact> recentContacts;
  
  /// 当前选中的联系人
  final ChatContact? selectedContact;
  
  /// 当前选中联系人的消息列表
  final List<ChatMessage> messages;
  
  /// 是否正在发送消息
  final bool isSending;
  
  /// 构造函数
  ChatListViewState({
    this.isLoading = false,
    this.errorMessage,
    this.allContacts = const [],
    this.favoriteContacts = const [],
    this.agentContacts = const [],
    this.doctorContacts = const [],
    this.providerContacts = const [],
    this.recentContacts = const [],
    this.selectedContact,
    this.messages = const [],
    this.isSending = false,
  });
  
  /// 复制并修改状态
  ChatListViewState copyWith({
    bool? isLoading,
    String? errorMessage,
    List<ChatContact>? allContacts,
    List<ChatContact>? favoriteContacts,
    List<ChatContact>? agentContacts,
    List<ChatContact>? doctorContacts,
    List<ChatContact>? providerContacts,
    List<ChatContact>? recentContacts,
    ChatContact? selectedContact,
    List<ChatMessage>? messages,
    bool? isSending,
  }) {
    return ChatListViewState(
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
      allContacts: allContacts ?? this.allContacts,
      favoriteContacts: favoriteContacts ?? this.favoriteContacts,
      agentContacts: agentContacts ?? this.agentContacts,
      doctorContacts: doctorContacts ?? this.doctorContacts,
      providerContacts: providerContacts ?? this.providerContacts,
      recentContacts: recentContacts ?? this.recentContacts,
      selectedContact: selectedContact ?? this.selectedContact,
      messages: messages ?? this.messages,
      isSending: isSending ?? this.isSending,
    );
  }
}

/// 聊天列表视图模型
class ChatListViewModel extends StateNotifier<ChatListViewState> {
  /// 聊天仓库
  final ChatRepository _chatRepository;
  
  /// 构造函数
  ChatListViewModel(this._chatRepository) : super(ChatListViewState()) {
    _initialize();
  }
  
  /// 初始化
  Future<void> _initialize() async {
    try {
      state = state.copyWith(isLoading: true);
      
      // 获取所有联系人数据
      final allContacts = await _chatRepository.getAllContacts();
      final favoriteContacts = await _chatRepository.getFavoriteContacts();
      final agentContacts = await _chatRepository.getAgentContacts();
      final doctorContacts = await _chatRepository.getDoctorContacts();
      final providerContacts = await _chatRepository.getProviderContacts();
      final recentContacts = await _chatRepository.getRecentContacts(10);
      
      state = state.copyWith(
        isLoading: false,
        allContacts: allContacts,
        favoriteContacts: favoriteContacts,
        agentContacts: agentContacts,
        doctorContacts: doctorContacts,
        providerContacts: providerContacts,
        recentContacts: recentContacts,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '初始化聊天列表失败: ${e.toString()}',
      );
    }
  }
  
  /// 刷新数据
  Future<void> refreshContacts() async {
    await _initialize();
  }
  
  /// 选择联系人
  Future<void> selectContact(String contactId) async {
    try {
      state = state.copyWith(isLoading: true);
      
      // 获取联系人
      final contact = state.allContacts.firstWhere((c) => c.id == contactId);
      
      // 获取消息
      final messages = await _chatRepository.getChatMessages(contactId);
      
      // 将消息标记为已读
      await _chatRepository.markMessagesAsRead(contactId);
      
      // 更新未读数
      final updatedContact = contact.copyWith(unreadCount: 0);
      
      // 更新联系人列表中的联系人
      final allContactsUpdated = state.allContacts.map((c) => 
        c.id == contactId ? updatedContact : c
      ).toList();
      
      // 更新最近联系人列表
      final recentContactsUpdated = state.recentContacts.map((c) => 
        c.id == contactId ? updatedContact : c
      ).toList();
      
      state = state.copyWith(
        isLoading: false,
        selectedContact: updatedContact,
        messages: messages,
        allContacts: allContactsUpdated,
        recentContacts: recentContactsUpdated,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '选择联系人失败: ${e.toString()}',
      );
    }
  }
  
  /// 发送消息
  Future<void> sendMessage(String content) async {
    if (state.selectedContact == null || content.trim().isEmpty) {
      return;
    }
    
    try {
      state = state.copyWith(isSending: true);
      
      // 发送消息
      final message = await _chatRepository.sendMessage(
        state.selectedContact!.id, 
        content,
      );
      
      // 更新消息列表
      final messages = [message, ...state.messages];
      
      // 更新联系人最后消息
      final updatedContact = state.selectedContact!.copyWith(
        lastMessage: content,
        lastActiveTime: DateTime.now(),
      );
      
      // 更新联系人列表
      final allContactsUpdated = state.allContacts.map((c) => 
        c.id == updatedContact.id ? updatedContact : c
      ).toList();
      
      // 更新最近联系人列表，并确保当前联系人排在最前面
      final recentContactsUpdated = [
        updatedContact,
        ...state.recentContacts.where((c) => c.id != updatedContact.id),
      ];
      
      state = state.copyWith(
        isSending: false,
        selectedContact: updatedContact,
        messages: messages,
        allContacts: allContactsUpdated,
        recentContacts: recentContactsUpdated,
      );
    } catch (e) {
      state = state.copyWith(
        isSending: false,
        errorMessage: '发送消息失败: ${e.toString()}',
      );
    }
  }
  
  /// 添加联系人到收藏
  Future<void> addToFavorites(String contactId) async {
    try {
      // 向仓库添加收藏
      await _chatRepository.addContactToFavorites(contactId);
      
      // 获取联系人
      final contact = state.allContacts.firstWhere((c) => c.id == contactId);
      
      // 更新收藏列表
      final favoriteContacts = [...state.favoriteContacts, contact];
      
      state = state.copyWith(
        favoriteContacts: favoriteContacts,
      );
    } catch (e) {
      state = state.copyWith(
        errorMessage: '添加收藏失败: ${e.toString()}',
      );
    }
  }
  
  /// 从收藏中移除联系人
  Future<void> removeFromFavorites(String contactId) async {
    try {
      // 向仓库移除收藏
      await _chatRepository.removeContactFromFavorites(contactId);
      
      // 更新收藏列表
      final favoriteContacts = state.favoriteContacts
          .where((c) => c.id != contactId)
          .toList();
      
      state = state.copyWith(
        favoriteContacts: favoriteContacts,
      );
    } catch (e) {
      state = state.copyWith(
        errorMessage: '移除收藏失败: ${e.toString()}',
      );
    }
  }
  
  /// 搜索联系人
  Future<List<ChatContact>> searchContacts(String query) async {
    if (query.trim().isEmpty) {
      return [];
    }
    
    try {
      return await _chatRepository.searchContacts(query);
    } catch (e) {
      state = state.copyWith(
        errorMessage: '搜索联系人失败: ${e.toString()}',
      );
      return [];
    }
  }
  
  /// 清除错误信息
  void clearError() {
    if (state.errorMessage != null) {
      state = state.copyWith(errorMessage: null);
    }
  }
} 