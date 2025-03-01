import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../domain/entities/message.dart';
import '../../../../ai_agents/models/ai_agent.dart';
import '../../../widgets/message_bubble.dart';

class ChatMessageList extends ConsumerWidget {
  final List<Message> messages;
  final String currentUserId;
  final Map<String, AIAgent> agents;
  final ScrollController? scrollController;
  final Function(Message)? onMessageLongPress;
  final bool isLoading;
  
  const ChatMessageList({
    Key? key,
    required this.messages,
    required this.currentUserId,
    required this.agents,
    this.scrollController,
    this.onMessageLongPress,
    this.isLoading = false,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Stack(
      children: [
        messages.isEmpty
            ? _buildEmptyState(context)
            : ListView.builder(
                controller: scrollController,
                padding: const EdgeInsets.symmetric(vertical: 16.0),
                reverse: true, // 新消息在底部
                itemCount: messages.length,
                itemBuilder: (context, index) {
                  final message = messages[index];
                  final isFromCurrentUser = message.senderId == currentUserId;
                  final AIAgent? agent = isFromCurrentUser 
                      ? null 
                      : agents[message.senderId];
                  
                  return MessageBubble(
                    message: message,
                    isFromCurrentUser: isFromCurrentUser,
                    agent: agent,
                    onLongPress: onMessageLongPress != null
                        ? () => onMessageLongPress!(message)
                        : null,
                  );
                },
              ),
        if (isLoading)
          Positioned(
            left: 0,
            right: 0,
            bottom: 8,
            child: Center(
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 8,
                ),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(
                          Theme.of(context).colorScheme.primary,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    const Text('正在思考...'),
                  ],
                ),
              ),
            ),
          ),
      ],
    );
  }
  
  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.chat_bubble_outline,
            size: 64,
            color: Theme.of(context).disabledColor,
          ),
          const SizedBox(height: 16),
          Text(
            '开始一段新的对话',
            style: TextStyle(
              fontSize: 16,
              color: Theme.of(context).disabledColor,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '您可以询问健康、养生相关的问题',
            style: TextStyle(
              fontSize: 14,
              color: Theme.of(context).disabledColor,
            ),
          ),
        ],
      ),
    );
  }
}