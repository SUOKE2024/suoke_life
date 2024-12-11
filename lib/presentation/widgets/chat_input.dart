import 'package:flutter/material.dart';

class ChatInput extends StatefulWidget {
  final Function(String) onTextSubmit;
  final VoidCallback onVoiceStart;
  final VoidCallback onVoiceEnd;
  final VoidCallback onVoiceCancel;
  final bool isRecording;

  const ChatInput({
    Key? key,
    required this.onTextSubmit,
    required this.onVoiceStart,
    required this.onVoiceEnd,
    required this.onVoiceCancel,
    required this.isRecording,
  }) : super(key: key);

  @override
  State<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends State<ChatInput> {
  final TextEditingController _textController = TextEditingController();
  bool _isComposing = false;

  void _handleSubmitted(String text) {
    widget.onTextSubmit(text);
    _textController.clear();
    setState(() {
      _isComposing = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        border: Border(
          top: BorderSide(
            color: Theme.of(context).dividerColor,
          ),
        ),
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
          child: Row(
            children: [
              // 语音按钮
              IconButton(
                icon: Icon(
                  widget.isRecording ? Icons.mic_off : Icons.mic,
                  color: widget.isRecording
                      ? Theme.of(context).colorScheme.error
                      : null,
                ),
                onPressed: widget.isRecording
                    ? widget.onVoiceCancel
                    : widget.onVoiceStart,
              ),
              // 文本输入框
              Expanded(
                child: TextField(
                  controller: _textController,
                  onChanged: (text) {
                    setState(() {
                      _isComposing = text.isNotEmpty;
                    });
                  },
                  onSubmitted: _handleSubmitted,
                  decoration: InputDecoration(
                    hintText: '输入消息...',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(20),
                      borderSide: BorderSide.none,
                    ),
                    filled: true,
                    fillColor: Theme.of(context).colorScheme.surface,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 8,
                    ),
                  ),
                  maxLines: null,
                  keyboardType: TextInputType.multiline,
                  textInputAction: TextInputAction.newline,
                  enabled: !widget.isRecording,
                ),
              ),
              // 发送按钮
              if (_isComposing)
                IconButton(
                  icon: Icon(
                    Icons.send,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  onPressed: () => _handleSubmitted(_textController.text),
                )
              else
                // 更多功能按钮
                IconButton(
                  icon: const Icon(Icons.add_circle_outline),
                  onPressed: () {
                    // TODO: 显示更多功能菜单
                    // - 图片
                    // - 文件
                    // - 位置
                    // - 联系人
                  },
                ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }
} 