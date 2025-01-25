import 'package:flutter/material.dart';
import 'package:suoke_life/core/services/infrastructure/local_storage_service.dart';
import 'package:suoke_life/core/network/llm_service_client.dart';
import 'package:suoke_life/features/home/lib/ai_agent_bubble.dart';
import 'package:get_it/get_it.dart';

class ChatInteractionPage extends StatefulWidget {
  const ChatInteractionPage({Key? key}) : super(key: key);

  @override
  _ChatInteractionPageState createState() => _ChatInteractionPageState();
}

class _ChatInteractionPageState extends State<ChatInteractionPage> {
  final _textController = TextEditingController();
  final List<ChatMessage> _messages = [];
  final LocalStorageService _localStorageService = GetIt.instance.get<LocalStorageService>();
  final LLMServiceClient _llmServiceClient = GetIt.instance.get<LLMServiceClient>();

  @override
  void initState() {
    super.initState();
    _loadChatHistory();
  }

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  Future<void> _loadChatHistory() async {
    final history = await _localStorageService.getChatHistory();
    setState(() {
      _messages.addAll(history.map((e) => ChatMessage(text: e['text'], isUser: e['isUser'])));
    });
  }

  Future<void> _saveChatHistory() async {
    final history = _messages.map((e) => {'text': e.text, 'isUser': e.isUser}).toList();
    await _localStorageService.saveChatHistory(history);
  }

  void _sendMessage() async {
    final text = _textController.text;
    if (text.isEmpty) return;

    setState(() {
      _messages.add(ChatMessage(text: text, isUser: true));
    });
    _textController.clear();
    _saveChatHistory();

    try {
      final response = await _llmServiceClient.generateText(text);
      setState(() {
        _messages.add(ChatMessage(text: response, isUser: false));
      });
      _saveChatHistory();
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(text: 'Error: $e', isUser: false));
      });
      _saveChatHistory();
    }
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
            child: SingleChildScrollView(
              child: ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _messages.length,
                itemBuilder: (context, index) {
                  final message = _messages[index];
                  return AiAgentBubble(
                    message: message.text,
                    isUser: message.isUser,
                  );
                },
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _textController,
                    decoration: const InputDecoration(
                      hintText: 'Type a message...',
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
        ],
      ),
    );
  }
}

class ChatMessage {
  final String text;
  final bool isUser;

  ChatMessage({required this.text, required this.isUser});
} 