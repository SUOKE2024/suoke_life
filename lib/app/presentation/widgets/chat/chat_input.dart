import 'package:flutter/material.dart';

class ChatInput extends StatefulWidget {
  final Function(String) onSend;
  final VoidCallback onVoice;

  const ChatInput({
    Key? key,
    required this.onSend,
    required this.onVoice,
  }) : super(key: key);

  @override
  State<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends State<ChatInput> {
  final _controller = TextEditingController();
  bool _isRecording = false;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(8),
      child: Row(
        children: [
          IconButton(
            icon: Icon(_isRecording ? Icons.stop : Icons.mic),
            onPressed: () {
              setState(() => _isRecording = !_isRecording);
              widget.onVoice();
            },
          ),
          Expanded(
            child: TextField(
              controller: _controller,
              decoration: InputDecoration(
                hintText: '输入消息...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 8,
                ),
              ),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.send),
            onPressed: () {
              if (_controller.text.isNotEmpty) {
                widget.onSend(_controller.text);
                _controller.clear();
              }
            },
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
} 