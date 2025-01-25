import 'package:flutter/material.dart';

class ChatInputBar extends StatefulWidget {
  final Function(String) onSend;
  final VoidCallback onVoice;
  final VoidCallback onAttachment;

  const ChatInputBar({
    Key? key,
    required this.onSend,
    required this.onVoice,
    required this.onAttachment,
  }) : super(key: key);

  @override
  State<ChatInputBar> createState() => _ChatInputBarState();
}

class _ChatInputBarState extends State<ChatInputBar> {
  final _controller = TextEditingController();
  bool _isVoiceMode = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black12,
            offset: const Offset(0, -1),
            blurRadius: 4,
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            IconButton(
              icon: Icon(_isVoiceMode ? Icons.keyboard : Icons.mic),
              onPressed: () {
                setState(() {
                  _isVoiceMode = !_isVoiceMode;
                });
              },
            ),
            if (_isVoiceMode)
              Expanded(
                child: GestureDetector(
                  onLongPressStart: (_) => widget.onVoice(),
                  child: Container(
                    height: 40,
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Center(
                      child: Text('按住说话'),
                    ),
                  ),
                ),
              )
            else
              Expanded(
                child: TextField(
                  controller: _controller,
                  decoration: const InputDecoration(
                    hintText: '输入消息...',
                    border: InputBorder.none,
                  ),
                ),
              ),
            IconButton(
              icon: const Icon(Icons.add),
              onPressed: widget.onAttachment,
            ),
            if (!_isVoiceMode)
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
      ),
    );
  }
} 