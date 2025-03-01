import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../ai_agents/models/ai_agent.dart';
import '../../../di/providers/chat_providers.dart';
import 'components/chat_input_bar.dart';
import 'components/chat_message_list.dart';

@RoutePage()
class ChatTabScreen extends ConsumerStatefulWidget {
  const ChatTabScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<ChatTabScreen> createState() => _ChatTabScreenState();
}

class _ChatTabScreenState extends ConsumerState<ChatTabScreen> {
  final ScrollController _scrollController = ScrollController();
  
  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatStateProvider);
    final chatNotifier = ref.read(chatStateProvider.notifier);
    
    // 创建代理映射
    final Map<String, AIAgent> agentMap = {
      AIAgent.xiaoai.id: AIAgent.xiaoai,
      AIAgent.laoke.id: AIAgent.laoke,
      AIAgent.xiaoke.id: AIAgent.xiaoke,
      AIAgent.system.id: AIAgent.system,
    };

    return Scaffold(
      appBar: AppBar(
        title: const Text('聊天'),
        centerTitle: true,
        actions: [
          PopupMenuButton<AIAgent>(
            icon: const Icon(Icons.change_circle),
            tooltip: '切换AI助手',
            onSelected: (AIAgent agent) {
              chatNotifier.switchAgent(agent);
            },
            itemBuilder: (BuildContext context) {
              return AIAgent.allAgents.map((AIAgent agent) {
                return PopupMenuItem<AIAgent>(
                  value: agent,
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 12,
                        backgroundColor: agent.color.withOpacity(0.2),
                        child: Text(
                          agent.name.substring(0, 1),
                          style: TextStyle(
                            color: agent.color,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(agent.name),
                    ],
                  ),
                );
              }).toList();
            },
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert),
            onSelected: (String value) {
              if (value == 'clear') {
                chatNotifier.clearMessages();
              }
            },
            itemBuilder: (BuildContext context) {
              return [
                const PopupMenuItem<String>(
                  value: 'clear',
                  child: Row(
                    children: [
                      Icon(Icons.delete_sweep, size: 20),
                      SizedBox(width: 8),
                      Text('清空聊天'),
                    ],
                  ),
                ),
              ];
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ChatMessageList(
              messages: chatState.messages,
              currentUserId: chatNotifier.currentUserId,
              agents: agentMap,
              scrollController: _scrollController,
              isLoading: chatState.isLoading,
            ),
          ),
          ChatInputBar(
            onSendText: (String text) {
              chatNotifier.sendMessage(text);
            },
            onAttachmentPressed: () {
              // TODO: 实现附件功能
            },
            onCameraPressed: () {
              // TODO: 实现相机功能
            },
            onMicPressed: () {
              // TODO: 实现语音输入功能
            },
            isLoading: chatState.isLoading,
          ),
        ],
      ),
    );
  }
}