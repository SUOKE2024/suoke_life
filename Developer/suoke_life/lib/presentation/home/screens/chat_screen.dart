import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/data/models/agent_model.dart';
import 'package:suoke_life/data/models/session_model.dart';
import 'package:suoke_life/presentation/home/providers/agent_state_provider.dart';
import 'package:suoke_life/core/widgets/animated_gradient_card.dart';
import 'package:suoke_life/core/widgets/animated_press_button.dart';
import 'package:suoke_life/core/widgets/skeleton_loading.dart';

/// 聊天屏幕
class ChatScreen extends ConsumerStatefulWidget {
  /// 构造函数
  const ChatScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  // 根据智能体ID获取对应的主题色
  Color getAgentThemeColor(String? agentId) {
    if (agentId == null) return AppColors.primaryColor;
    
    switch (agentId) {
      case 'xiaoke-service':
        return Colors.blue.shade600;
      case 'xiaoai-service':
        return AppColors.primaryColor;
      case 'soer-service':
        return Colors.purple.shade600;
      case 'laoke-service':
        return Colors.amber.shade800;
      default:
        return AppColors.primaryColor;
    }
  }

  @override
  void initState() {
    super.initState();
    // 加载智能体列表
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(agentStateProvider.notifier).loadAgents();
    });
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  void _sendMessage() {
    if (_messageController.text.trim().isNotEmpty) {
      final message = _messageController.text.trim();
      _messageController.clear();
      // 发送消息
      ref.read(agentStateProvider.notifier).sendStreamMessage(message);
      // 滚动到底部
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _scrollToBottom();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(agentStateProvider);
    final agentThemeColor = getAgentThemeColor(state.currentAgent?.id);
    
    return Scaffold(
      appBar: AppBar(
        title: state.currentAgent != null 
            ? Row(
                children: [
                  Text(state.currentAgent!.name),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 6,
                      vertical: 2,
                    ),
                    decoration: BoxDecoration(
                      color: agentThemeColor.withAlpha(50),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      state.currentAgent!.type,
                      style: TextStyle(
                        fontSize: 12,
                        color: agentThemeColor,
                      ),
                    ),
                  ),
                ],
              )
            : const Text('选择智能体'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.read(agentStateProvider.notifier).loadAgents();
            },
          ),
        ],
      ),
      drawer: _buildAgentDrawer(state),
      body: Column(
        children: [
          // 消息列表
          Expanded(
            child: state.errorMessage != null
                ? _buildErrorWidget(state.errorMessage!)
                : state.isLoading && state.messages == null
                    ? _buildLoadingWidget()
                    : _buildMessageList(state),
          ),
          // 输入框
          _buildMessageInput(agentThemeColor),
        ],
      ),
    );
  }

  Widget _buildAgentDrawer(AgentState state) {
    return Drawer(
      child: Column(
        children: [
          const DrawerHeader(
            decoration: BoxDecoration(
              color: AppColors.primaryColor,
            ),
            child: Center(
              child: Text(
                '索克生活',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          Expanded(
            child: state.agents == null || state.agents!.isEmpty
                ? state.isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : const Center(child: Text('没有可用的智能体'))
                : ListView.builder(
                    itemCount: state.agents!.length,
                    itemBuilder: (context, index) {
                      final agent = state.agents![index];
                      return _buildAgentListItem(agent, state);
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildAgentListItem(AgentModel agent, AgentState state) {
    final isSelected = state.currentAgent?.id == agent.id;
    final agentColor = getAgentThemeColor(agent.id);
    
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: agentColor.withAlpha(50),
        child: Text(
          agent.name.substring(0, 1),
          style: TextStyle(
            color: agentColor,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
      title: Text(agent.name),
      subtitle: Text(agent.type),
      selected: isSelected,
      onTap: () {
        ref.read(agentStateProvider.notifier).selectAgent(agent);
        Navigator.pop(context); // 关闭抽屉
      },
    );
  }

  Widget _buildMessageList(AgentState state) {
    final messages = state.messages;
    final currentAgent = state.currentAgent;
    final agentThemeColor = getAgentThemeColor(currentAgent?.id);
    
    if (messages == null || messages.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.chat_bubble_outline, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            const Text(
              '没有消息',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
            const SizedBox(height: 32),
            if (currentAgent != null)
              AnimatedGradientCard(
                colors: [
                  agentThemeColor,
                  agentThemeColor.withAlpha(150),
                ],
                borderRadius: BorderRadius.circular(16),
                height: 100,
                width: 300,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.smart_toy, color: Colors.white),
                      const SizedBox(height: 8),
                      Text(
                        '与${currentAgent.name}开始对话',
                        style: const TextStyle(
                          fontSize: 16,
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      );
    }
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _scrollToBottom();
    });
    
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: messages.length,
      itemBuilder: (context, index) {
        final message = messages[index];
        return _buildMessageItem(message, agentThemeColor);
      },
    );
  }

  Widget _buildMessageItem(MessageModel message, Color agentColor) {
    final isUser = message.role == 'user';
    
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isUser 
              ? AppColors.primaryColor.withAlpha(230)
              : agentColor.withAlpha(50),
          borderRadius: BorderRadius.circular(16),
        ),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        child: Text(
          message.content,
          style: TextStyle(
            color: isUser ? Colors.white : Colors.black,
          ),
        ),
      ),
    );
  }

  Widget _buildMessageInput(Color agentColor) {
    final state = ref.watch(agentStateProvider);
    final bool isAgentSelected = state.currentAgent != null;
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withAlpha(50),
            blurRadius: 4,
            offset: const Offset(0, -1),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _messageController,
              decoration: InputDecoration(
                hintText: isAgentSelected ? '输入消息...' : '请先选择智能体',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide.none,
                ),
                fillColor: Colors.grey.shade100,
                filled: true,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 8,
                ),
                enabled: isAgentSelected && !state.isLoading,
              ),
              onSubmitted: (_) => _sendMessage(),
            ),
          ),
          const SizedBox(width: 8),
          AnimatedPressButton(
            onPressed: isAgentSelected && !state.isLoading ? _sendMessage : null,
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isAgentSelected && !state.isLoading
                    ? agentColor
                    : Colors.grey,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.send,
                color: Colors.white,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingWidget() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SkeletonLoading(
            height: 60,
            width: MediaQuery.of(context).size.width * 0.6,
            borderRadius: 16,
          ),
          const SizedBox(height: 24),
          SkeletonLoading(
            height: 60,
            width: MediaQuery.of(context).size.width * 0.7,
            borderRadius: 16,
          ),
          const SizedBox(height: 24),
          Align(
            alignment: Alignment.centerRight,
            child: SkeletonLoading(
              height: 60,
              width: MediaQuery.of(context).size.width * 0.5,
              borderRadius: 16,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorWidget(String errorMessage) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.error_outline,
            color: Colors.red,
            size: 48,
          ),
          const SizedBox(height: 16),
          Text(
            errorMessage,
            style: const TextStyle(
              color: Colors.red,
              fontSize: 16,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () {
              ref.read(agentStateProvider.notifier).loadAgents();
            },
            child: const Text('重试'),
          ),
        ],
      ),
    );
  }
} 