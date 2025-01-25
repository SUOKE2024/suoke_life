import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import '../../../features/ai/services/ai_service.dart';
import '../../../core/di/injection.dart';

@RoutePage()
class ChatPage extends StatefulWidget {
  final String assistantId;

  const ChatPage({
    super.key,
    @PathParam('assistantId') required this.assistantId,
  });

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final _aiService = getIt<AIService>();
  final _textController = TextEditingController();
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('与${widget.assistantId}对话'),
        leading: const AutoLeadingButton(),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              // TODO: 实现聊天消息列表
            ),
          ),
          _buildInputBar(),
        ],
      ),
    );
  }

  Widget _buildInputBar() {
    return SafeArea(
      child: Container(
        padding: const EdgeInsets.all(8.0),
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _textController,
                decoration: const InputDecoration(
                  hintText: '输入消息...',
                  border: OutlineInputBorder(),
                ),
              ),
            ),
            IconButton(
              icon: const Icon(Icons.send),
              onPressed: _sendMessage,
            ),
          ],
        ),
      ),
    );
  }

  void _sendMessage() {
    // TODO: 实现发送消息
  }
} 