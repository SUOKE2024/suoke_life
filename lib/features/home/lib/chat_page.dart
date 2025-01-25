import 'package:flutter/material.dart';
import 'package:suoke_life/core/services/ai_service.dart';
import 'package:suoke_life/core/services/chat_service.dart';
import 'package:suoke_life/core/models/chat_message.dart';
import 'package:suoke_life/ui_components/buttons/app_button.dart';
import 'package:suoke_life/ui_components/cards/app_card.dart';
import 'package:suoke_life/features/home/lib/ai_agent_bubble.dart';
import 'package:get_it/get_it.dart';

class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  _ChatPageState createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final TextEditingController _textController = TextEditingController();
  final List<ChatMessage> _messages = [];
  final AiService _aiService = GetIt.instance<AiService>();
  final ChatService _chatService = GetIt.instance<ChatService>();

  @override
  void initState() {
    super.initState();
    _loadChatHistory();
  }

  Future<void> _loadChatHistory() async {
    final history = await _chatService.getChatHistory();
    setState(() {
      _messages.addAll(history);
    });
  }

  void _sendMessage() async {
    final messageText = _textController.text.trim();
    if (messageText.isNotEmpty) {
      final userMessage = ChatMessage(
        text: messageText,
        isUser: true,
        timestamp: DateTime.now(),
      );
      setState(() {
        _messages.add(userMessage);
      });
      _textController.clear();

      final aiResponse = await _aiService.generateResponse(messageText);
      final aiMessage = ChatMessage(
        text: aiResponse,
        isUser: false,
        timestamp: DateTime.now(),
      );
      setState(() {
        _messages.add(aiMessage);
      });
      await _chatService.saveChatMessage(userMessage);
      await _chatService.saveChatMessage(aiMessage);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Chat')),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
                  child: message.isUser
                      ? _buildUserMessage(message)
                      : AiAgentBubble(message: message.text),
                );
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _textController,
                    decoration: const InputDecoration(hintText: 'Type a message...'),
                  ),
                ),
                AppButton(
                  text: 'Send',
                  onPressed: _sendMessage,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildUserMessage(ChatMessage message) {
    return Align(
      alignment: Alignment.centerRight,
      child: AppCard(
        child: Text(message.text),
      ),
    );
  }
} 