import 'package:flutter/material.dart';

import '../../services/chat_service.dart';
import '../widgets/chat_bubble.dart';

class ChatTestPage extends StatefulWidget {
  const ChatTestPage({super.key});

  @override
  State<ChatTestPage> createState() => _ChatTestPageState();
}

class _ChatTestPageState extends State<ChatTestPage> {
  final _textController = TextEditingController();
  final _scrollController = ScrollController();
  bool _showMetadata = false;
  bool _isComposing = false;

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    if (!_scrollController.hasClients) return;
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    });
  }

  void _handleSubmitted(String text, ChatService chatService) {
    if (text.trim().isEmpty) return;
    
    _textController.clear();
    setState(() => _isComposing = false);
    chatService.sendMessage(text).then((_) => _scrollToBottom());
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => ChatService(),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('聊天测试'),
          actions: [
            IconButton(
              icon: Icon(_showMetadata ? Icons.visibility_off : Icons.visibility),
              onPressed: () {
                setState(() {
                  _showMetadata = !_showMetadata;
                });
              },
              tooltip: '显示/隐藏元数据',
            ),
          ],
        ),
        body: Consumer<ChatService>(
          builder: (context, chatService, child) {
            return Column(
              children: [
                Expanded(
                  child: GestureDetector(
                    onTap: () => FocusScope.of(context).unfocus(),
                    child: ListView.builder(
                      controller: _scrollController,
                      padding: const EdgeInsets.symmetric(vertical: 8),
                      itemCount: chatService.messages.length,
                      itemBuilder: (context, index) {
                        final message = chatService.messages[index];
                        return ChatBubble(
                          key: ValueKey(message.id),
                          message: message,
                          showMetadata: _showMetadata,
                        );
                      },
                    ),
                  ),
                ),
                const Divider(height: 1),
                Container(
                  decoration: BoxDecoration(
                    color: Theme.of(context).cardColor,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.05),
                        offset: const Offset(0, -1),
                        blurRadius: 3,
                      ),
                    ],
                  ),
                  child: SafeArea(
                    child: Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Row(
                        children: [
                          Expanded(
                            child: TextField(
                              controller: _textController,
                              decoration: InputDecoration(
                                hintText: '输入消息...',
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(20),
                                ),
                                contentPadding: const EdgeInsets.symmetric(
                                  horizontal: 16,
                                  vertical: 10,
                                ),
                                filled: true,
                                fillColor: Theme.of(context).colorScheme.surface,
                              ),
                              maxLines: null,
                              textInputAction: TextInputAction.send,
                              onChanged: (text) {
                                setState(() {
                                  _isComposing = text.trim().isNotEmpty;
                                });
                              },
                              onSubmitted: (text) => _handleSubmitted(
                                text,
                                chatService,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          AnimatedContainer(
                            duration: const Duration(milliseconds: 200),
                            child: IconButton(
                              icon: chatService.isLoading
                                  ? const SizedBox(
                                      width: 24,
                                      height: 24,
                                      child: CircularProgressIndicator(strokeWidth: 2),
                                    )
                                  : Icon(
                                      Icons.send,
                                      color: _isComposing
                                          ? Theme.of(context).colorScheme.primary
                                          : Theme.of(context).disabledColor,
                                    ),
                              onPressed: chatService.isLoading || !_isComposing
                                  ? null
                                  : () => _handleSubmitted(
                                        _textController.text,
                                        chatService,
                                      ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
} 