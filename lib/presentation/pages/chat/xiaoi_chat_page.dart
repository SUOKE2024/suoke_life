import 'package:flutter/material.dart';
import '../../../intelligence/assistants/xiaoi/xiaoi_service.dart';
import '../../../services/voice_service.dart';
import '../../widgets/chat_message.dart';
import '../../widgets/chat_input.dart';
import '../../widgets/voice_wave_animation.dart';
import '../../../models/message.dart';

class XiaoiChatPage extends StatefulWidget {
  final XiaoiService xiaoiService;
  final VoiceService voiceService;

  const XiaoiChatPage({
    Key? key,
    required this.xiaoiService,
    required this.voiceService,
  }) : super(key: key);

  @override
  State<XiaoiChatPage> createState() => _XiaoiChatPageState();
}

class _XiaoiChatPageState extends State<XiaoiChatPage> {
  final List<Message> _messages = [];
  bool _isLoading = false;
  bool _isRecording = false;
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _loadInitialMessages();
  }

  Future<void> _loadInitialMessages() async {
    setState(() => _isLoading = true);
    try {
      final history = await widget.xiaoiService.getConversationHistory(
        'current_user_id',
        limit: 20,
      );
      setState(() {
        _messages.addAll(history);
        _isLoading = false;
      });
      _scrollToBottom();
    } catch (e) {
      setState(() => _isLoading = false);
      _showError('加载历史消息失败');
    }
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

  Future<void> _handleTextSubmit(String text) async {
    if (text.trim().isEmpty) return;

    final userMessage = Message(
      content: text,
      role: 'user',
      timestamp: DateTime.now(),
    );

    setState(() {
      _messages.add(userMessage);
      _isLoading = true;
    });
    _scrollToBottom();

    try {
      final response = await widget.xiaoiService.processMessage(userMessage);
      setState(() {
        _messages.add(response);
        _isLoading = false;
      });
      _scrollToBottom();
    } catch (e) {
      setState(() => _isLoading = false);
      _showError('发送消息失败');
    }
  }

  Future<void> _handleVoiceStart() async {
    try {
      await widget.voiceService.startRecording();
      setState(() => _isRecording = true);
    } catch (e) {
      _showError('启动录音失败');
    }
  }

  Future<void> _handleVoiceEnd() async {
    if (!_isRecording) return;

    setState(() => _isLoading = true);
    try {
      final voiceData = await widget.voiceService.stopRecording();
      setState(() => _isRecording = false);

      // 创建语音消息
      final userMessage = Message(
        content: '语音消息',
        role: 'user',
        timestamp: DateTime.now(),
        voiceData: voiceData,
      );

      setState(() => _messages.add(userMessage));
      _scrollToBottom();

      // 处理语音消息
      final response = await widget.xiaoiService.processMessage(userMessage);
      setState(() {
        _messages.add(response);
        _isLoading = false;
      });
      _scrollToBottom();
    } catch (e) {
      setState(() {
        _isRecording = false;
        _isLoading = false;
      });
      _showError('处理语音消息失败');
    }
  }

  Future<void> _handleVoiceCancel() async {
    try {
      await widget.voiceService.cancelRecording();
    } catch (e) {
      _showError('取消录音失败');
    } finally {
      setState(() => _isRecording = false);
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('小艾'),
            Text(
              '您的贴心生活助理',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.info_outline),
            onPressed: () {
              // TODO: 显示小艾的详细信息和功能说明
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Stack(
              children: [
                ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: _messages.length,
                  itemBuilder: (context, index) {
                    final message = _messages[index];
                    return ChatMessage(
                      message: message,
                      onRetry: message.role == 'user'
                          ? () => _handleTextSubmit(message.content)
                          : null,
                    );
                  },
                ),
                if (_isLoading)
                  const Positioned(
                    bottom: 0,
                    left: 0,
                    right: 0,
                    child: LinearProgressIndicator(),
                  ),
              ],
            ),
          ),
          if (_isRecording)
            Container(
              padding: const EdgeInsets.all(16),
              color: Theme.of(context).colorScheme.surface,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('正在录音...'),
                  const SizedBox(height: 8),
                  const VoiceWaveAnimation(),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      TextButton(
                        onPressed: _handleVoiceCancel,
                        child: const Text('取消'),
                      ),
                      const SizedBox(width: 16),
                      ElevatedButton(
                        onPressed: _handleVoiceEnd,
                        child: const Text('完成'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ChatInput(
            onTextSubmit: _handleTextSubmit,
            onVoiceStart: _handleVoiceStart,
            onVoiceEnd: _handleVoiceEnd,
            onVoiceCancel: _handleVoiceCancel,
            isRecording: _isRecording,
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }
} 