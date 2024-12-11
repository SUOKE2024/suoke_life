import 'package:flutter/material.dart';
import '../../../services/business_ai_assistant_service.dart';
import '../../../core/di/service_locator.dart';

class BusinessAssistantPage extends StatefulWidget {
  const BusinessAssistantPage({super.key});

  @override
  State<BusinessAssistantPage> createState() => _BusinessAssistantPageState();
}

class _BusinessAssistantPageState extends State<BusinessAssistantPage> {
  final _businessAIAssistant = serviceLocator<BusinessAIAssistantService>();
  final _messageController = TextEditingController();
  final List<ChatMessage> _messages = [];
  bool _isLoading = false;

  final List<QuickQuestion> _quickQuestions = [
    QuickQuestion(
      icon: Icons.store,
      title: '如何入驻平台？',
      subtitle: '了解入驻流程和要求',
      action: (assistant) => assistant.guideSupplierOnboarding(),
    ),
    QuickQuestion(
      icon: Icons.add_business,
      title: '如何录入产品？',
      subtitle: '产品信息录入指南',
      action: (assistant) => assistant.guideProductEntry(),
    ),
    QuickQuestion(
      icon: Icons.policy,
      title: '平台政策',
      subtitle: '了解平台规则和标准',
      action: (assistant) => assistant.explainPolicies('平台政策概览'),
    ),
  ];

  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }

  void _addMessage(String content, bool isUser) {
    setState(() {
      _messages.add(ChatMessage(
        content: content,
        isUser: isUser,
        timestamp: DateTime.now(),
      ));
    });
  }

  Future<void> _handleQuickQuestion(QuickQuestion question) async {
    setState(() {
      _isLoading = true;
    });

    try {
      _addMessage(question.title, true);
      final response = await question.action(_businessAIAssistant);
      _addMessage(response, false);
    } catch (e) {
      _addMessage('抱歉，处理您的请求时出现错误，请稍后重试。', false);
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _handleUserMessage() async {
    final message = _messageController.text.trim();
    if (message.isEmpty) return;

    _messageController.clear();
    _addMessage(message, true);

    setState(() {
      _isLoading = true;
    });

    try {
      final response = await _businessAIAssistant.handleSupplierInquiry(message);
      _addMessage(response, false);
    } catch (e) {
      _addMessage('抱歉，处理您的请求时出现错误，请稍后重试。', false);
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI商务助手'),
        centerTitle: true,
      ),
      body: Column(
        children: [
          // 快捷问题区域
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surface,
              borderRadius: const BorderRadius.vertical(
                bottom: Radius.circular(16),
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '常见问题',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _quickQuestions.length,
                  separatorBuilder: (context, index) => const SizedBox(height: 8),
                  itemBuilder: (context, index) {
                    final question = _quickQuestions[index];
                    return InkWell(
                      onTap: () => _handleQuickQuestion(question),
                      borderRadius: BorderRadius.circular(8),
                      child: Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          border: Border.all(
                            color: Colors.grey.withOpacity(0.2),
                          ),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              question.icon,
                              color: Theme.of(context).primaryColor,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    question.title,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                  Text(
                                    question.subtitle,
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: Colors.grey[600],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const Icon(
                              Icons.chevron_right,
                              color: Colors.grey,
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),

          // 对话区域
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              reverse: true,
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[_messages.length - 1 - index];
                return Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: ChatBubble(message: message),
                );
              },
            ),
          ),

          // 加载指示器
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: LinearProgressIndicator(),
            ),

          // 输入区域
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surface,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 8,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: const InputDecoration(
                      hintText: '输入您的问题...',
                      border: OutlineInputBorder(),
                    ),
                    maxLines: null,
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _handleUserMessage(),
                  ),
                ),
                const SizedBox(width: 16),
                IconButton.filled(
                  onPressed: _handleUserMessage,
                  icon: const Icon(Icons.send),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class QuickQuestion {
  final IconData icon;
  final String title;
  final String subtitle;
  final Future<String> Function(BusinessAIAssistantService) action;

  const QuickQuestion({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.action,
  });
}

class ChatMessage {
  final String content;
  final bool isUser;
  final DateTime timestamp;

  const ChatMessage({
    required this.content,
    required this.isUser,
    required this.timestamp,
  });
}

class ChatBubble extends StatelessWidget {
  final ChatMessage message;

  const ChatBubble({
    super.key,
    required this.message,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment:
          message.isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
      children: [
        if (!message.isUser) ...[
          CircleAvatar(
            backgroundColor: Theme.of(context).primaryColor,
            child: const Icon(
              Icons.support_agent,
              color: Colors.white,
            ),
          ),
          const SizedBox(width: 8),
        ],
        Flexible(
          child: Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 12,
            ),
            decoration: BoxDecoration(
              color: message.isUser
                  ? Theme.of(context).primaryColor
                  : Theme.of(context).colorScheme.surface,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Text(
              message.content,
              style: TextStyle(
                color: message.isUser ? Colors.white : null,
              ),
            ),
          ),
        ),
        if (message.isUser) ...[
          const SizedBox(width: 8),
          CircleAvatar(
            backgroundColor: Colors.grey[300],
            child: const Icon(
              Icons.person,
              color: Colors.white,
            ),
          ),
        ],
      ],
    );
  }
} 