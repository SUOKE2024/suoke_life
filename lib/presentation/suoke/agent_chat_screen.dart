import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/models/agent_model.dart';
import 'package:suoke_life/presentation/suoke/view_models/agent_view_model.dart';
import 'package:suoke_life/presentation/suoke/widgets/agent_selector.dart';
import 'package:suoke_life/presentation/suoke/widgets/message_bubble.dart';
import 'package:suoke_life/presentation/suoke/widgets/message_input.dart';
import 'package:suoke_life/presentation/suoke/widgets/suggested_responses.dart';

/// 智能体聊天屏幕
class AgentChatScreen extends ConsumerWidget {
  /// 构造函数
  const AgentChatScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(agentViewModelProvider);
    final viewModel = ref.read(agentViewModelProvider.notifier);
    
    // 默认用户头像
    const String userAvatarUrl = 'assets/images/avatars/user_avatar.png';
    
    return Scaffold(
      appBar: AppBar(
        title: Text(state.selectedConversation?.title ?? '智能体对话'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => viewModel.createNewConversation(),
          ),
        ],
      ),
      body: state.isLoading && state.agents.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // 智能体选择器
                AgentSelector(
                  agents: state.agents,
                  selectedAgent: state.activeAgent,
                  onAgentSelected: (agentType) => viewModel.switchAgent(agentType),
                ),
                
                // 聊天消息列表
                Expanded(
                  child: state.messages.isEmpty
                      ? _buildEmptyChat(context, state.activeAgent)
                      : _buildChatMessages(
                          context, 
                          state.messages, 
                          state.activeAgent, 
                          userAvatarUrl,
                        ),
                ),
                
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
                          onPressed: viewModel.clearError,
                          iconSize: 16,
                        ),
                      ],
                    ),
                  ),
                
                // 建议回复
                if (state.suggestedResponses.isNotEmpty)
                  SuggestedResponses(
                    suggestions: state.suggestedResponses,
                    onResponseSelected: (response) => viewModel.useSuggestedResponse(response),
                    themeColor: state.activeAgent?.themeColor ?? Theme.of(context).colorScheme.primary,
                  ),
                
                // 消息输入
                MessageInput(
                  onSendMessage: (message) => viewModel.sendMessage(message),
                  themeColor: state.activeAgent?.themeColor ?? Theme.of(context).colorScheme.primary,
                  isLoading: state.isSending,
                  hintText: '发送消息给${state.activeAgent?.name ?? '智能体'}...',
                ),
              ],
            ),
    );
  }

  /// 构建空聊天界面
  Widget _buildEmptyChat(BuildContext context, Agent? activeAgent) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          if (activeAgent != null) ...[
            CircleAvatar(
              radius: 48,
              backgroundImage: AssetImage(activeAgent.avatarUrl),
            ),
            const SizedBox(height: 16),
            Text(
              activeAgent.name,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32),
              child: Text(
                activeAgent.description,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
            ),
          ] else ...[
            const Icon(
              Icons.chat_bubble_outline,
              size: 64,
              color: Colors.grey,
            ),
            const SizedBox(height: 16),
            Text(
              '开始与智能体对话',
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ],
          const SizedBox(height: 24),
          Text(
            '在下方输入框中发送消息，开始对话',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }

  /// 构建聊天消息列表
  Widget _buildChatMessages(
    BuildContext context, 
    List<AgentMessage> messages, 
    Agent? activeAgent,
    String userAvatarUrl,
  ) {
    return ListView.builder(
      padding: const EdgeInsets.only(top: 16, bottom: 8),
      reverse: true, // 最新消息在底部
      itemCount: messages.length,
      itemBuilder: (context, index) {
        // 反向列表，最新消息在底部
        final reversedIndex = messages.length - 1 - index;
        final message = messages[reversedIndex];
        
        // 如果是系统消息且需要隐藏，则不显示
        if (message.messageType == MessageType.system && 
            message.extraData != null && 
            message.extraData!['hidden'] == true) {
          return const SizedBox.shrink();
        }
        
        // 判断消息类型
        final isUserMessage = message.messageType == MessageType.user;
        final agentThemeColor = activeAgent?.themeColor;
        
        return MessageBubble(
          message: message,
          senderAvatarUrl: isUserMessage 
              ? userAvatarUrl 
              : activeAgent?.avatarUrl ?? 'assets/images/avatars/default_agent.png',
          isUserMessage: isUserMessage,
          agentThemeColor: agentThemeColor,
        );
      },
    );
  }
} 