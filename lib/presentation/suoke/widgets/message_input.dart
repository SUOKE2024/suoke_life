import 'package:flutter/material.dart';

/// 消息输入回调
typedef MessageInputCallback = void Function(String message);

/// 消息输入组件
class MessageInput extends StatefulWidget {
  /// 发送消息回调
  final MessageInputCallback onSendMessage;
  
  /// 主题色
  final Color themeColor;
  
  /// 是否显示录音按钮
  final bool showVoiceButton;
  
  /// 是否正在加载
  final bool isLoading;
  
  /// 占位文字
  final String hintText;

  /// 构造函数
  const MessageInput({
    Key? key,
    required this.onSendMessage,
    required this.themeColor,
    this.showVoiceButton = true,
    this.isLoading = false,
    this.hintText = '发送消息...',
  }) : super(key: key);

  @override
  State<MessageInput> createState() => _MessageInputState();
}

class _MessageInputState extends State<MessageInput> {
  final TextEditingController _controller = TextEditingController();
  bool _showVoiceRecord = false;
  bool _isRecording = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 3,
            offset: const Offset(0, -1),
          ),
        ],
      ),
      child: Row(
        children: [
          if (widget.showVoiceButton)
            IconButton(
              icon: Icon(
                _showVoiceRecord ? Icons.keyboard : Icons.mic,
                color: widget.themeColor,
              ),
              onPressed: () {
                setState(() {
                  _showVoiceRecord = !_showVoiceRecord;
                });
              },
            ),
          Expanded(
            child: _showVoiceRecord
                ? _buildVoiceButton()
                : _buildTextInput(),
          ),
          const SizedBox(width: 8),
          _buildSendButton(),
        ],
      ),
    );
  }

  /// 构建文本输入框
  Widget _buildTextInput() {
    return TextField(
      controller: _controller,
      decoration: InputDecoration(
        hintText: widget.hintText,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(24),
          borderSide: BorderSide.none,
        ),
        filled: true,
        fillColor: Theme.of(context).colorScheme.surfaceVariant,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),
      maxLines: 5,
      minLines: 1,
      textInputAction: TextInputAction.send,
      onSubmitted: (text) {
        if (text.trim().isNotEmpty && !widget.isLoading) {
          widget.onSendMessage(text);
          _controller.clear();
        }
      },
      onChanged: (text) {
        // 可以在这里添加输入监听，例如显示/隐藏发送按钮
        setState(() {});
      },
    );
  }

  /// 构建语音按钮
  Widget _buildVoiceButton() {
    return GestureDetector(
      onLongPressStart: (_) {
        setState(() {
          _isRecording = true;
        });
        // 开始录音的逻辑
        // 这里应调用实际的录音API
      },
      onLongPressEnd: (_) {
        setState(() {
          _isRecording = false;
        });
        // 结束录音并发送的逻辑
        // 这里应处理录音文件并调用发送回调
      },
      child: Container(
        height: 50,
        decoration: BoxDecoration(
          color: _isRecording 
              ? widget.themeColor.withOpacity(0.2) 
              : Theme.of(context).colorScheme.surfaceVariant,
          borderRadius: BorderRadius.circular(24),
        ),
        child: Center(
          child: Text(
            _isRecording ? '松开发送' : '按住说话',
            style: TextStyle(
              color: _isRecording 
                  ? widget.themeColor 
                  : Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
        ),
      ),
    );
  }

  /// 构建发送按钮
  Widget _buildSendButton() {
    final bool canSend = _controller.text.trim().isNotEmpty && !widget.isLoading;
    
    return IconButton(
      icon: widget.isLoading
          ? SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(widget.themeColor),
              ),
            )
          : Icon(
              Icons.send,
              color: canSend ? widget.themeColor : Colors.grey,
            ),
      onPressed: canSend
          ? () {
              widget.onSendMessage(_controller.text);
              _controller.clear();
            }
          : null,
    );
  }
} 