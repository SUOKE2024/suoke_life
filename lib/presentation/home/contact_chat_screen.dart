import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:suoke_life/domain/models/chat_contact_model.dart';
import 'package:suoke_life/domain/repositories/chat_repository.dart';

/// 联系人聊天页面
class ContactChatScreen extends ConsumerStatefulWidget {
  /// 构造函数
  const ContactChatScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<ContactChatScreen> createState() => _ContactChatScreenState();
}

class _ContactChatScreenState extends ConsumerState<ContactChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _isComposing = false;

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final state = ref.watch(chatListViewModelProvider);
    
    // 如果没有选中联系人，返回上一页
    if (state.selectedContact == null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.pop(context);
      });
      return const SizedBox.shrink();
    }
    
    final contact = state.selectedContact!;
    
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
        titleSpacing: 0,
        title: Row(
          children: [
            CircleAvatar(
              radius: 16,
              backgroundImage: AssetImage(contact.avatarUrl),
            ),
            const SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  contact.name,
                  style: theme.textTheme.titleMedium,
                ),
                Text(
                  _getContactStatusText(contact),
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.info_outline),
            onPressed: () {
              // TODO: 显示联系人详情
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('查看联系人资料功能即将上线')),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: () {
              _showChatOptions(context, contact);
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // 日期分隔线
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 8),
            child: Center(
              child: Chip(
                label: Text('今天'),
                backgroundColor: Color(0xFFEEEEEE),
              ),
            ),
          ),
          
          // 聊天消息列表
          Expanded(
            child: state.messages.isEmpty
                ? _buildEmptyChat(context, contact)
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                    reverse: true, // 最新消息在底部
                    itemCount: state.messages.length,
                    itemBuilder: (context, index) {
                      final message = state.messages[index];
                      return _buildMessageBubble(context, message, contact);
                    },
                  ),
          ),
          
          // 消息输入框
          _buildMessageInput(context),
        ],
      ),
    );
  }
  
  /// 获取联系人状态文本
  String _getContactStatusText(ChatContact contact) {
    if (contact.type == ChatContactType.doctor) {
      final isOnline = contact.extraData?['isOnline'] == true;
      return isOnline ? '在线' : '离线';
    }
    
    return contact.description;
  }
  
  /// 构建空聊天界面
  Widget _buildEmptyChat(BuildContext context, ChatContact contact) {
    final theme = Theme.of(context);
    
    String greeting;
    String hint;
    
    switch (contact.type) {
      case ChatContactType.agent:
        greeting = '您好，我是${contact.name}';
        hint = '有什么我可以帮您的吗？';
        break;
      case ChatContactType.doctor:
        greeting = '您好，我是${contact.name}';
        hint = '请问有什么健康问题需要咨询？';
        break;
      case ChatContactType.provider:
        greeting = '欢迎光临${contact.name}';
        hint = '有什么我们可以为您服务的吗？';
        break;
      case ChatContactType.user:
        greeting = '您已添加${contact.name}为好友';
        hint = '开始聊天吧';
        break;
    }
    
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircleAvatar(
            radius: 40,
            backgroundImage: AssetImage(contact.avatarUrl),
          ),
          const SizedBox(height: 16),
          Text(
            greeting,
            style: theme.textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          Text(
            hint,
            style: TextStyle(
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 32),
          ElevatedButton(
            onPressed: () {
              // 发送预设问候语
              _sendMessage('你好');
            },
            child: const Text('发送问候'),
          ),
        ],
      ),
    );
  }
  
  /// 构建消息气泡
  Widget _buildMessageBubble(BuildContext context, ChatMessage message, ChatContact contact) {
    final theme = Theme.of(context);
    final isUserMessage = message.senderId == 'current_user';
    
    // 设置不同类型联系人的主题色
    Color contactThemeColor;
    switch (contact.type) {
      case ChatContactType.agent:
        final agentTypeStr = contact.extraData?['agentType'] as String?;
        if (agentTypeStr != null) {
          if (agentTypeStr.contains('xiaoAi')) {
            contactThemeColor = const Color(0xFF35BB78); // 小艾：索克绿
          } else if (agentTypeStr.contains('xiaoKe')) {
            contactThemeColor = const Color(0xFF5E72E4); // 小克：蓝色
          } else if (agentTypeStr.contains('laoKe')) {
            contactThemeColor = const Color(0xFFDA6E2C); // 老克：橙棕色
          } else if (agentTypeStr.contains('suoEr')) {
            contactThemeColor = const Color(0xFFFF6800); // 索儿：索克橙
          } else {
            contactThemeColor = theme.colorScheme.primary;
          }
        } else {
          contactThemeColor = theme.colorScheme.primary;
        }
        break;
      case ChatContactType.doctor:
        contactThemeColor = const Color(0xFF6574F7); // 医生：专业蓝
        break;
      case ChatContactType.provider:
        contactThemeColor = const Color(0xFF4DABF5); // 供应商：鲜亮蓝
        break;
      case ChatContactType.user:
        contactThemeColor = const Color(0xFF9C9FA6); // 用户：灰色
        break;
    }
    
    // 格式化时间
    final timeString = DateFormat.Hm().format(message.sentTime);
    
    // 若是系统消息，显示为居中提示
    if (message.type == ChatMessageType.system) {
      return Container(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Center(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(16),
            ),
            child: Text(
              message.content,
              style: TextStyle(
                color: Colors.grey[800],
                fontSize: 12,
              ),
            ),
          ),
        ),
      );
    }
    
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        mainAxisAlignment: isUserMessage ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          // 联系人头像（非用户消息时显示）
          if (!isUserMessage) 
            CircleAvatar(
              radius: 16,
              backgroundImage: AssetImage(contact.avatarUrl),
            ),
          
          const SizedBox(width: 8),
          
          // 消息气泡
          Flexible(
            child: Column(
              crossAxisAlignment: isUserMessage ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  decoration: BoxDecoration(
                    color: isUserMessage 
                      ? theme.colorScheme.primary 
                      : Colors.grey[200],
                    borderRadius: BorderRadius.circular(18),
                  ),
                  child: Text(
                    message.content,
                    style: TextStyle(
                      color: isUserMessage ? Colors.white : Colors.black,
                    ),
                  ),
                ),
                
                // 发送时间
                Padding(
                  padding: const EdgeInsets.only(top: 4, left: 4, right: 4),
                  child: Text(
                    timeString,
                    style: TextStyle(
                      fontSize: 10,
                      color: Colors.grey[600],
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(width: 8),
          
          // 用户头像（用户消息时显示）
          if (isUserMessage) 
            const CircleAvatar(
              radius: 16,
              backgroundImage: AssetImage('assets/images/avatars/user_avatar.png'),
            ),
        ],
      ),
    );
  }
  
  /// 构建消息输入区域
  Widget _buildMessageInput(BuildContext context) {
    final theme = Theme.of(context);
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            blurRadius: 4,
            offset: const Offset(0, -1),
          ),
        ],
      ),
      child: Row(
        children: [
          // 附加功能按钮
          IconButton(
            icon: const Icon(Icons.add),
            color: Colors.grey[600],
            onPressed: () {
              // TODO: 实现附加功能菜单
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('更多功能即将上线')),
              );
            },
          ),
          
          // 输入框
          Expanded(
            child: TextField(
              controller: _messageController,
              decoration: InputDecoration(
                hintText: '发送消息...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide.none,
                ),
                filled: true,
                fillColor: Colors.grey[100],
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              ),
              textCapitalization: TextCapitalization.sentences,
              onChanged: (text) {
                setState(() {
                  _isComposing = text.trim().isNotEmpty;
                });
              },
            ),
          ),
          
          // 发送按钮
          IconButton(
            icon: Icon(
              _isComposing ? Icons.send : Icons.mic,
              color: _isComposing ? theme.colorScheme.primary : Colors.grey[600],
            ),
            onPressed: _isComposing
                ? () => _sendMessage(_messageController.text)
                : () {
                    // TODO: 实现语音输入
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('语音输入功能即将上线')),
                    );
                  },
          ),
        ],
      ),
    );
  }
  
  /// 发送消息
  void _sendMessage(String text) {
    if (text.trim().isEmpty) return;
    
    final viewModel = ref.read(chatListViewModelProvider.notifier);
    viewModel.sendMessage(text);
    
    _messageController.clear();
    setState(() {
      _isComposing = false;
    });
    
    // 滚动到底部
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          0,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }
  
  /// 显示聊天选项
  void _showChatOptions(BuildContext context, ChatContact contact) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.search),
                title: const Text('搜索聊天记录'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: 实现搜索聊天记录
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('搜索聊天记录功能即将上线')),
                  );
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
              if (contact.type == ChatContactType.doctor)
                ListTile(
                  leading: const Icon(Icons.calendar_today),
                  title: const Text('预约咨询'),
                  onTap: () {
                    Navigator.pop(context);
                    // TODO: 实现预约咨询
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('预约咨询功能即将上线')),
                    );
                  },
                ),
              ListTile(
                leading: const Icon(Icons.clear_all),
                title: const Text('清空聊天记录'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: 实现清空聊天记录
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('清空聊天记录功能即将上线')),
                  );
                },
              ),
            ],
          ),
        );
      },
    );
  }
} 