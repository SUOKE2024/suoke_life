import 'package:flutter/material.dart';
import 'package:get/get.dart';

class AIChatInput extends StatefulWidget {
  final Function(String) onSendText;
  final Function(String) onSendVoice;

  const AIChatInput({
    Key? key,
    required this.onSendText,
    required this.onSendVoice,
  }) : super(key: key);

  @override
  State<AIChatInput> createState() => _AIChatInputState();
}

class _AIChatInputState extends State<AIChatInput> {
  final textController = TextEditingController();
  bool isVoiceMode = false;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        border: Border(
          top: BorderSide(color: Colors.grey[300]!),
        ),
      ),
      child: Row(
        children: [
          IconButton(
            icon: Icon(isVoiceMode ? Icons.keyboard : Icons.mic),
            onPressed: () {
              setState(() {
                isVoiceMode = !isVoiceMode;
              });
            },
          ),
          Expanded(
            child: isVoiceMode
                ? _buildVoiceButton()
                : TextField(
                    controller: textController,
                    decoration: InputDecoration(
                      hintText: '输入消息...',
                      border: InputBorder.none,
                    ),
                  ),
          ),
          IconButton(
            icon: Icon(Icons.send),
            onPressed: () {
              final text = textController.text.trim();
              if (text.isNotEmpty) {
                widget.onSendText(text);
                textController.clear();
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _buildVoiceButton() {
    return GestureDetector(
      onLongPressStart: (_) {
        // 开始录音
      },
      onLongPressEnd: (_) {
        // 结束录音并发送
      },
      child: Container(
        height: 50,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: Colors.grey[200],
          borderRadius: BorderRadius.circular(4),
        ),
        child: Text('按住说话'),
      ),
    );
  }

  @override
  void dispose() {
    textController.dispose();
    super.dispose();
  }
} 