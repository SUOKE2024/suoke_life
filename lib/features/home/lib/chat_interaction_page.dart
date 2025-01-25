import 'package:flutter/material.dart';
import 'package:suoke_life/features/home/lib/ai_agent_bubble.dart';
import 'package:suoke_life/core/services/infrastructure/local_storage_service.dart';
import 'package:get_it/get_it.dart';

class ChatInteractionPage extends StatefulWidget {
  const ChatInteractionPage({Key? key}) : super(key: key);

  @override
  State<ChatInteractionPage> createState() => _ChatInteractionPageState();
}

class _ChatInteractionPageState extends State<ChatInteractionPage> {
  final _textController = TextEditingController();
  final _scrollController = ScrollController();
  final _localStorageService = GetIt.instance.get<LocalStorageService>();
  List<Map<String, dynamic>> _chatMessages = [];

  @override
  void initState() {
    super.initState();
    _loadChatHistory();
  }

  Future<void> _loadChatHistory() async {
    final chats = await _localStorageService.getChats();
    setState(() {
      _chatMessages = chats;
    });
  }

  void _sendMessage() async {
    final text = _textController.text;
    if (text.isNotEmpty) {
      await _localStorageService.insertChat(text, true);
      setState(() {
        _chatMessages.add({'text': text, 'isUser': 1});
      });
      _textController.clear();
      _scrollToBottom();
      // Simulate AI response
      await Future.delayed(const Duration(seconds: 1));
      final aiResponse = 'AI: I received your message: $text';
      await _localStorageService.insertChat(aiResponse, false);
      setState(() {
        _chatMessages.add({'text': aiResponse, 'isUser': 0});
      });
      _scrollToBottom();
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Chat Interaction'),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              itemCount: _chatMessages.length,
              itemBuilder: (context, index) {
                final message = _chatMessages[index];
                return message['isUser'] == 1
                    ? _buildUserBubble(message['text'])
                    : AiAgentBubble(text: message['text']);
              },
            ),
          ),
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildUserBubble(String text) {
    return Align(
      alignment: Alignment.centerRight,
      child: Container(
        margin: const EdgeInsets.all(8.0),
        padding: const EdgeInsets.all(12.0),
        decoration: BoxDecoration(
          color: Colors.blue[200],
          borderRadius: BorderRadius.circular(12.0),
        ),
        child: Text(text),
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.all(8.0),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _textController,
              decoration: const InputDecoration(
                hintText: 'Type a message...',
              ),
              onSubmitted: (_) => _sendMessage(),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.send),
            onPressed: _sendMessage,
          ),
        ],
      ),
    );
  }
} 