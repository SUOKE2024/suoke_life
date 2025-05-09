import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:suoke_life/domain/models/chat_contact_model.dart';
import 'package:suoke_life/presentation/home/view_models/chat_list_view_model.dart';
import 'package:suoke_life/presentation/home/widgets/chat_contact_item.dart';
import 'package:suoke_life/presentation/home/widgets/favorite_contacts_row.dart';

/// 首页屏幕
class HomeScreen extends ConsumerStatefulWidget {
  /// 构造函数
  const HomeScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  final TextEditingController _searchController = TextEditingController();
  List<ChatContact> _searchResults = [];
  bool _isSearching = false;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final state = ref.watch(chatListViewModelProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: _isSearching 
          ? _buildSearchField()
          : const Text('聊天'),
        actions: [
          IconButton(
            icon: Icon(_isSearching ? Icons.close : Icons.search),
            onPressed: () {
              setState(() {
                if (_isSearching) {
                  _searchController.clear();
                  _searchResults = [];
                }
                _isSearching = !_isSearching;
              });
            },
          ),
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () {
              // TODO: 实现添加联系人功能
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('添加新聊天功能即将上线')),
              );
            },
          ),
        ],
      ),
      body: state.isLoading && state.allContacts.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: () => ref.read(chatListViewModelProvider.notifier).refreshContacts(),
              child: Column(
                children: [
                  // 错误提示
                  if (state.errorMessage != null)
                    Container(
                      padding: const EdgeInsets.all(8),
                      color: Colors.red.shade100,
                      child: Row(
                        children: [
                          const Icon(Icons.error, color: Colors.red),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              state.errorMessage!,
                              style: const TextStyle(color: Colors.red),
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.close, color: Colors.red),
                            onPressed: () => ref.read(chatListViewModelProvider.notifier).clearError(),
                            iconSize: 16,
                          ),
                        ],
                      ),
                    ),
                  
                  // 收藏联系人横向列表
                  if (!_isSearching && state.favoriteContacts.isNotEmpty)
                    FavoriteContactsRow(
                      contacts: state.favoriteContacts,
                      onContactTap: _openChatScreen,
                    ),
                  
                  // 主聊天列表
                  Expanded(
                    child: _isSearching && _searchController.text.isNotEmpty
                        ? _buildSearchResults()
                        : ListView(
                            padding: const EdgeInsets.only(top: 8),
                            children: [
                              // 分隔线
                              if (!_isSearching && state.favoriteContacts.isNotEmpty)
                                const Padding(
                                  padding: EdgeInsets.symmetric(horizontal: 16),
                                  child: Divider(),
                                ),
                                
                              // 最近联系人标题
                              if (!_isSearching)
                                Padding(
                                  padding: const EdgeInsets.only(left: 16, right: 16, top: 8, bottom: 4),
                                  child: Text(
                                    '最近聊天',
                                    style: theme.textTheme.titleSmall?.copyWith(
                                      color: theme.colorScheme.secondary,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              
                              // 聊天联系人列表
                              ...state.recentContacts.map((contact) => 
                                ChatContactItem(
                                  contact: contact,
                                  onTap: () => _openChatScreen(contact),
                                  onLongPress: () => _showContactOptions(contact),
                                ),
                              ),
                              
                              // 其他联系人
                              if (!_isSearching && state.recentContacts.isNotEmpty)
                                Padding(
                                  padding: const EdgeInsets.only(left: 16, right: 16, top: 16, bottom: 4),
                                  child: Text(
                                    '其他联系人',
                                    style: theme.textTheme.titleSmall?.copyWith(
                                      color: theme.colorScheme.secondary,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              
                              // 分类：智能体
                              if (!_isSearching && state.agentContacts.isNotEmpty)
                                _buildContactGroup('智能体', state.agentContacts),
                              
                              // 分类：名医
                              if (!_isSearching && state.doctorContacts.isNotEmpty)
                                _buildContactGroup('名医', state.doctorContacts),
                              
                              // 分类：服务供应商
                              if (!_isSearching && state.providerContacts.isNotEmpty)
                                _buildContactGroup('服务与产品', state.providerContacts),
                            ],
                          ),
                  ),
                ],
              ),
            ),
    );
  }
  
  /// 构建联系人分组
  Widget _buildContactGroup(String title, List<ChatContact> contacts) {
    if (contacts.isEmpty) return const SizedBox.shrink();
    
    // 过滤掉已经在最近联系人中显示的联系人，避免重复
    final recentContactIds = ref.read(chatListViewModelProvider).recentContacts
        .map((contact) => contact.id)
        .toList();
        
    final filteredContacts = contacts
        .where((contact) => !recentContactIds.contains(contact.id))
        .toList();
        
    if (filteredContacts.isEmpty) return const SizedBox.shrink();
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 16, top: 12, bottom: 4),
          child: Text(
            title,
            style: TextStyle(
              color: Colors.grey[600],
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        ...filteredContacts.map((contact) => 
          ChatContactItem(
            contact: contact,
            onTap: () => _openChatScreen(contact),
            onLongPress: () => _showContactOptions(contact),
          ),
        ),
      ],
    );
  }
  
  /// 构建搜索输入框
  Widget _buildSearchField() {
    return TextField(
      controller: _searchController,
      decoration: const InputDecoration(
        hintText: '搜索联系人...',
        border: InputBorder.none,
        hintStyle: TextStyle(color: Colors.grey),
      ),
      style: const TextStyle(color: Colors.black),
      autofocus: true,
      onChanged: _performSearch,
    );
  }
  
  /// 执行搜索
  void _performSearch(String query) async {
    if (query.isEmpty) {
      setState(() {
        _searchResults = [];
      });
      return;
    }
    
    final results = await ref.read(chatListViewModelProvider.notifier).searchContacts(query);
    
    setState(() {
      _searchResults = results;
    });
  }
  
  /// 构建搜索结果列表
  Widget _buildSearchResults() {
    if (_searchResults.isEmpty) {
      return const Center(
        child: Text('未找到相关联系人'),
      );
    }
    
    return ListView.builder(
      itemCount: _searchResults.length,
      itemBuilder: (context, index) {
        final contact = _searchResults[index];
        return ChatContactItem(
          contact: contact,
          onTap: () => _openChatScreen(contact),
          onLongPress: () => _showContactOptions(contact),
        );
      },
    );
  }
  
  /// 打开聊天界面
  void _openChatScreen(ChatContact contact) {
    // 先选择联系人
    ref.read(chatListViewModelProvider.notifier).selectContact(contact.id);
    
    // 导航到聊天页面
    Navigator.pushNamed(context, '/contact_chat');
  }
  
  /// 显示联系人操作选项
  void _showContactOptions(ChatContact contact) {
    final viewModel = ref.read(chatListViewModelProvider.notifier);
    final isFavorite = ref.read(chatListViewModelProvider).favoriteContacts
        .any((c) => c.id == contact.id);
    
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.person),
                title: Text(contact.name),
                subtitle: Text(contact.description),
              ),
              const Divider(),
              ListTile(
                leading: Icon(isFavorite ? Icons.star : Icons.star_border),
                title: Text(isFavorite ? '取消收藏' : '添加收藏'),
                onTap: () {
                  Navigator.pop(context);
                  if (isFavorite) {
                    viewModel.removeFromFavorites(contact.id);
                  } else {
                    viewModel.addToFavorites(contact.id);
                  }
                },
              ),
              if (contact.type == ChatContactType.provider)
                ListTile(
                  leading: const Icon(Icons.storefront),
                  title: const Text('访问服务页面'),
                  onTap: () {
                    Navigator.pop(context);
                    // TODO: 导航到SUOKE频道并定位到对应供应商
                    Navigator.pushNamed(context, '/suoke', arguments: {'providerId': contact.id});
                  },
                ),
            ],
          ),
        );
      },
    );
  }
}
