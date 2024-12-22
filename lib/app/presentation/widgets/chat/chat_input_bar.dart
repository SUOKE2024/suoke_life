import 'package:flutter/material.dart';

class ChatInputBar extends StatefulWidget {
  final void Function(String) onSendText;
  final VoidCallback? onVoiceStart;
  final VoidCallback? onVoiceEnd;
  final VoidCallback? onVoiceCancel;
  final VoidCallback? onTapExtra;

  const ChatInputBar({
    Key? key,
    required this.onSendText,
    this.onVoiceStart,
    this.onVoiceEnd,
    this.onVoiceCancel,
    this.onTapExtra,
  }) : super(key: key);

  @override
  State<ChatInputBar> createState() => _ChatInputBarState();
}

class _ChatInputBarState extends State<ChatInputBar> {
  final TextEditingController _textController = TextEditingController();
  bool _isVoiceMode = false;

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  void _handleSend() {
    final text = _textController.text.trim();
    if (text.isNotEmpty) {
      widget.onSendText(text);
      _textController.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, -1),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            // 语音/键盘切换按钮
            if (widget.onVoiceStart != null)
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
                  ? GestureDetector(
                      onTapDown: (_) => widget.onVoiceStart?.call(),
                      onTapUp: (_) => widget.onVoiceEnd?.call(),
                      onTapCancel: () => widget.onVoiceCancel?.call(),
                      child: Container(
                        height: 36,
                        decoration: BoxDecoration(
                          color: Colors.grey[200],
                          borderRadius: BorderRadius.circular(18),
                        ),
                        alignment: Alignment.center,
                        child: const Text('按住说话'),
                      ),
                    )
                  : TextField(
                      controller: _textController,
                      decoration: const InputDecoration(
                        hintText: '输入消息...',
                        border: InputBorder.none,
                        contentPadding: EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 8,
                        ),
                      ),
                      maxLines: null,
                    ),
            ),
            // 发送/更多按钮
            IconButton(
              icon: const Icon(Icons.send),
              onPressed: _handleSend,
            ),
            if (widget.onTapExtra != null)
              IconButton(
                icon: const Icon(Icons.add_circle_outline),
                onPressed: widget.onTapExtra,
              ),
          ],
        ),
      ),
    );
  }
} 