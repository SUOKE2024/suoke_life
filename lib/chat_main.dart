import 'package:flutter/material.dart';
import 'intelligence/assistants/laoke/laoke_service.dart';
import 'services/ai/core_algorithm_service.dart';
import 'services/storage/data_storage_service.dart';
import 'models/message.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '老克助手',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const ChatTestPage(),
    );
  }
}

class ChatTestPage extends StatefulWidget {
  const ChatTestPage({Key? key}) : super(key: key);

  @override
  State<ChatTestPage> createState() => _ChatTestPageState();
}

class _ChatTestPageState extends State<ChatTestPage> {
  late final LaokeService _laokeService;
  final List<Message> _messages = [];
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _initializeServices();
    _sendInitialMessage();
  }

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _initializeServices() {
    _laokeService = LaokeService(
      algorithmService: CoreAlgorithmService(),
      storageService: DataStorageService(),
    );
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

  Future<void> _sendMessage(String text) async {
    if (text.trim().isEmpty) return;

    final message = Message(
      content: text,
      role: 'user',
      timestamp: DateTime.now(),
    );

    setState(() {
      _messages.add(message);
      _isLoading = true;
      _textController.clear();
    });
    _scrollToBottom();

    try {
      final response = await _laokeService.processMessage(message);
      setState(() {
        _messages.add(response);
        _isLoading = false;
      });
      _scrollToBottom();
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('发送消息失败: $e')),
        );
      }
    }
  }

  Future<void> _sendInitialMessage() async {
    final message = Message(
      content: '老克 晚上好 吃好了吗',
      role: 'user',
      timestamp: DateTime.now(),
    );

    setState(() {
      _messages.add(message);
      _isLoading = true;
    });

    try {
      final response = await _laokeService.processMessage(message);
      setState(() {
        _messages.add(response);
        _isLoading = false;
      });
      _scrollToBottom();
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('发送消息失败: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('与老克对话'),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    mainAxisAlignment: message.role == 'user'
                        ? MainAxisAlignment.end
                        : MainAxisAlignment.start,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: message.role == 'user'
                              ? Theme.of(context).colorScheme.primary
                              : Theme.of(context).colorScheme.surfaceVariant,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          message.content,
                          style: TextStyle(
                            color: message.role == 'user'
                                ? Theme.of(context).colorScheme.onPrimary
                                : Theme.of(context).colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(16),
              child: CircularProgressIndicator(),
            ),
          Padding(
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
                    onSubmitted: _sendMessage,
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: () => _sendMessage(_textController.text),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
} 