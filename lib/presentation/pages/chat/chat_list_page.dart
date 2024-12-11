import 'package:flutter/material.dart';
import '../../../models/chat_model.dart';
import '../../widgets/chat_list_item.dart';

class ChatListPage extends StatelessWidget {
  const ChatListPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('聊天'),
        actions: [
          IconButton(
            icon: const Badge(
              label: Text('2'),
              child: Icon(Icons.notifications_none),
            ),
            onPressed: () {
              Navigator.pushNamed(context, '/notifications');
            },
          ),
          IconButton(
            icon: const Icon(Icons.add_circle_outline),
            onPressed: () {
              _showAddDialog(context);
            },
          ),
        ],
      ),
      body: CustomScrollView(
        slivers: [
          // AI助手置顶区域
          SliverToBoxAdapter(
            child: Container(
              padding: const EdgeInsets.all(16),
              color: Theme.of(context).colorScheme.surfaceVariant.withOpacity(0.3),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'AI助手',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      _buildAIAssistantItem(
                        context,
                        name: '索儿',
                        avatar: 'assets/images/soer.png',
                        onTap: () => Navigator.pushNamed(context, '/chat/soer'),
                      ),
                      const SizedBox(width: 16),
                      _buildAIAssistantItem(
                        context,
                        name: '老克',
                        avatar: 'assets/images/claude.png',
                        onTap: () => Navigator.pushNamed(context, '/chat/claude'),
                      ),
                      const SizedBox(width: 16),
                      _buildAIAssistantItem(
                        context,
                        name: '小克',
                        avatar: 'assets/images/suoke.png',
                        onTap: () => Navigator.pushNamed(context, '/chat/suoke'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          // 聊天列表
          SliverList(
            delegate: SliverChildBuilderDelegate(
              (context, index) {
                final chat = _getMockChats()[index];
                return ChatListItem(
                  avatar: chat.avatar,
                  name: chat.name,
                  lastMessage: chat.lastMessage,
                  timestamp: chat.timestamp,
                  unreadCount: chat.unreadCount,
                  onTap: () => Navigator.pushNamed(
                    context,
                    '/chat/detail',
                    arguments: chat,
                  ),
                );
              },
              childCount: _getMockChats().length,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAIAssistantItem(
    BuildContext context, {
    required String name,
    required String avatar,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        children: [
          CircleAvatar(
            radius: 24,
            backgroundImage: AssetImage(avatar),
          ),
          const SizedBox(height: 4),
          Text(
            name,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ],
      ),
    );
  }

  void _showAddDialog(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ListTile(
            leading: const Icon(Icons.person_add),
            title: const Text('添加好友'),
            onTap: () {
              Navigator.pop(context);
              Navigator.pushNamed(context, '/contacts/add');
            },
          ),
          ListTile(
            leading: const Icon(Icons.group_add),
            title: const Text('创建群聊'),
            onTap: () {
              Navigator.pop(context);
              Navigator.pushNamed(context, '/group/create');
            },
          ),
          ListTile(
            leading: const Icon(Icons.medical_services),
            title: const Text('咨询专家'),
            onTap: () {
              Navigator.pop(context);
              Navigator.pushNamed(context, '/expert/consult');
            },
          ),
        ],
      ),
    );
  }

  List<ChatModel> _getMockChats() {
    return [
      ChatModel(
        id: '1',
        name: '张医生',
        avatar: 'assets/images/avatars/doctor1.png',
        lastMessage: '好的，我们下周三见。',
        timestamp: DateTime.now().subtract(const Duration(minutes: 5)),
        unreadCount: 0,
        type: ChatType.expert,
      ),
      ChatModel(
        id: '2',
        name: '营养师李教授',
        avatar: 'assets/images/avatars/nutritionist1.png',
        lastMessage: '这是您的营养方案，请查收。',
        timestamp: DateTime.now().subtract(const Duration(hours: 1)),
        unreadCount: 1,
        type: ChatType.expert,
      ),
      ChatModel(
        id: '3',
        name: '健康咨询群',
        avatar: 'assets/images/avatars/group1.png',
        lastMessage: '[图片]',
        timestamp: DateTime.now().subtract(const Duration(hours: 2)),
        unreadCount: 3,
        type: ChatType.group,
      ),
      // 添加更多模拟数据...
    ];
  }
} 