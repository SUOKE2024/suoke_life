import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../data/models/chat_conversation.dart';
import '../../../core/config/assistant_config.dart';
import './assistant_chat_page.dart';

class AssistantSelectPage extends StatelessWidget {
  const AssistantSelectPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('选择助手')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildAssistantCard(context, AssistantConfig.xiaoai),
          _buildAssistantCard(context, AssistantConfig.laoke),
          _buildAssistantCard(context, AssistantConfig.xiaoke),
        ],
      ),
    );
  }

  Widget _buildAssistantCard(BuildContext context, Map<String, String> config) {
    return Card(
      child: ListTile(
        leading: CircleAvatar(
          backgroundImage: AssetImage(config['avatar']!),
        ),
        title: Text(config['name']!),
        subtitle: Text(config['description']!),
        onTap: () {
          final conversation = ChatConversation(
            id: DateTime.now().millisecondsSinceEpoch,
            title: '与${config['name']}的对话',
            model: config['model']!,
            avatar: config['avatar']!,
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          );
          
          Navigator.push(() => AssistantChatPage(conversation: conversation));
        },
      ),
    );
  }
} 