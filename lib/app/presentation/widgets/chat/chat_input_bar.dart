import 'package:flutter/material.dart';

class ChatInputBar extends StatefulWidget {
  final Function(String) onSendText;
  final VoidCallback onVoiceStart;
  final VoidCallback onVoiceEnd;
  final VoidCallback onVoiceCancel;
  final VoidCallback onTapExtra;

  const ChatInputBar({
    Key? key,
    required this.onSendText,
    required this.onVoiceStart,
    required this.onVoiceEnd,
    required this.onVoiceCancel,
    required this.onTapExtra,
  }) : super(key: key);

  @override
  State<ChatInputBar> createState() => _ChatInputBarState();
}

class _ChatInputBarState extends State<ChatInputBar> {
  final _textController = TextEditingController();
  bool _isVoiceMode = false;

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Theme.of(context).scaffoldBackgroundColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          // 语音/键盘切换按钮
          IconButton(
            icon: Icon(_isVoiceMode ? Icons.keyboard : Icons.mic),
            onPressed: () {
              setState(() {
                _isVoiceMode = !_isVoiceMode;
              });
            },
          ),
          // 输入区域
          Expanded(
            child: _isVoiceMode
                ? _buildVoiceButton()
                : _buildTextInput(),
          ),
          // 额外功能按钮
          IconButton(
            icon: const Icon(Icons.add_circle_outline),
            onPressed: widget.onTapExtra,
          ),
        ],
      ),
    );
  }

  Widget _buildTextInput() {
    return TextField(
      controller: _textController,
      decoration: InputDecoration(
        hintText: '输入消息...',
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(20),
          borderSide: BorderSide.none,
        ),
        filled: true,
        fillColor: Colors.grey[200],
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 8,
        ),
        suffixIcon: IconButton(
          icon: const Icon(Icons.send),
          onPressed: () {
            if (_textController.text.isNotEmpty) {
              widget.onSendText(_textController.text);
              _textController.clear();
            }
          },
        ),
      ),
    );
  }

  Widget _buildVoiceButton() {
    return GestureDetector(
      onLongPressStart: (_) => widget.onVoiceStart(),
      onLongPressEnd: (_) => widget.onVoiceEnd(),
      onLongPressCancel: widget.onVoiceCancel,
      child: Container(
        height: 40,
        decoration: BoxDecoration(
          color: Colors.grey[200],
          borderRadius: BorderRadius.circular(20),
        ),
        child: const Center(
          child: Text('按住说话'),
        ),
      ),
    );
  }
} 