import 'package:flutter/material.dart';
import 'package:suoke_life/lib/core/services/ai_service.dart';
import 'package:suoke_life/lib/core/services/chat_service.dart';
import 'package:suoke_life/lib/core/models/chat_message.dart';
import 'package:suoke_life/ui_components/buttons/app_button.dart';
import 'package:suoke_life/ui_components/cards/app_card.dart';
import 'package:suoke_life/features/home/lib/ai_agent_bubble.dart';
import 'package:get_it/get_it.dart';
import 'package:provider/provider.dart';
import 'package:suoke_life/lib/core/widgets/common_app_button.dart';
import 'package:suoke_life/lib/core/widgets/common_app_card.dart';
import 'package:go_router/go_router.dart';
import 'package:suoke_life/lib/core/widgets/common_bottom_navigation_bar.dart';

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
  int _currentIndex = 0;

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

  void _onTabTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return CommonScaffold(
      title: 'Chats',
      body: ListView(
        children: const [
          ChatListItem(
            title: 'Xiaoai',
            lastMessage: 'Hello, how can I help you?',
            time: '10:00 AM',
          ),
          ChatListItem(
            title: 'Xiaoke',
            lastMessage: 'What are you doing today?',
            time: 'Yesterday',
          ),
          ChatListItem(
            title: 'Laoke',
            lastMessage: 'What is the meaning of life?',
            time: '2 days ago',
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          context.go('/chat_interaction');
        },
        child: const Icon(Icons.add),
      ),
      bottomNavigationBar: CommonBottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
      ),
    );
  }
} 