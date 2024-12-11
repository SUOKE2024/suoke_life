import 'package:flutter/material.dart';
import '../../services/chat_service.dart';
import '../../models/chat_message.dart';
import '../widgets/chat_message_widget.dart';
import '../widgets/chat_input.dart';
import '../widgets/biometric_feedback_widget.dart';

class ChatPage extends StatefulWidget {
  const ChatPage({Key? key}) : super(key: key);

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  late final ChatService _chatService;
  final ScrollController _scrollController = ScrollController();
  bool _showBiometricFeedback = true;

  @override
  void initState() {
    super.initState();
    _chatService = ChatService();
    
    // 监听消息流以自动滚动
    _chatService.messageStream.listen((_) {
      _scrollToBottom();
    });
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('索克生活助手'),
        actions: [
          IconButton(
            icon: Icon(_showBiometricFeedback ? Icons.visibility : Icons.visibility_off),
            onPressed: () {
              setState(() {
                _showBiometricFeedback = !_showBiometricFeedback;
              });
            },
            tooltip: '显示/隐藏生物特征反馈',
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: _chatService.clearMessages,
            tooltip: '清空聊天记录',
          ),
        ],
      ),
      body: Column(
        children: [
          if (_showBiometricFeedback)
            BiometricFeedbackWidget(
              biometricStream: _chatService.biometricStream,
            ),
          Expanded(
            child: ListenableBuilder(
              listenable: _chatService,
              builder: (context, _) {
                return ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: _chatService.messages.length,
                  itemBuilder: (context, index) {
                    final message = _chatService.messages[index];
                    return ChatMessageWidget(
                      message: message,
                      showBiometricData: _showBiometricFeedback,
                    );
                  },
                );
              },
            ),
          ),
          ChatInput(
            onSendMessage: (content) async {
              await _chatService.sendMessage(content);
            },
            isLoading: _chatService.isLoading,
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _chatService.dispose();
    super.dispose();
  }
} 