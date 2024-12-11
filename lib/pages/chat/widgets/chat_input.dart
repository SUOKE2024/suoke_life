import 'package:flutter/material.dart';

class ChatInput extends StatefulWidget {
  final Function(String) onSendText;
  final VoidCallback onStartVoice;
  final VoidCallback onStopVoice;
  final VoidCallback onSendImage;
  final VoidCallback onSendFile;
  final bool showCamera;
  final bool showAddButton;

  const ChatInput({
    Key? key,
    required this.onSendText,
    required this.onStartVoice,
    required this.onStopVoice,
    required this.onSendImage,
    required this.onSendFile,
    this.showCamera = false,
    this.showAddButton = false,
  }) : super(key: key);

  @override
  State<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends State<ChatInput> {
  final _textController = TextEditingController();
  bool _isVoiceMode = false;
  bool _showMoreOptions = false;

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
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SafeArea(
            child: Row(
              children: [
                // 相机/语音切换按钮
                if (widget.showCamera)
                  IconButton(
                    icon: const Icon(Icons.camera_alt),
                    onPressed: widget.onSendImage,
                    tooltip: '拍照',
                  )
                else
                  IconButton(
                    icon: Icon(_isVoiceMode ? Icons.keyboard : Icons.mic),
                    onPressed: () {
                      setState(() => _isVoiceMode = !_isVoiceMode);
                    },
                    tooltip: _isVoiceMode ? '键盘' : '语音',
                  ),
                
                // 输入区域
                Expanded(
                  child: _isVoiceMode
                      ? _buildVoiceButton()
                      : TextField(
                          controller: _textController,
                          decoration: const InputDecoration(
                            hintText: '输入消息...',
                            border: InputBorder.none,
                          ),
                          maxLines: null,
                          textInputAction: TextInputAction.send,
                          onSubmitted: (_) => _handleSend(),
                        ),
                ),

                // 更多功能按钮
                if (widget.showAddButton)
                  IconButton(
                    icon: const Icon(Icons.add_circle_outline),
                    onPressed: () {
                      setState(() => _showMoreOptions = !_showMoreOptions);
                    },
                    tooltip: '更多',
                  )
                else
                  IconButton(
                    icon: const Icon(Icons.image),
                    onPressed: widget.onSendImage,
                    tooltip: '图片',
                  ),

                // 发送按钮
                if (!_isVoiceMode)
                  IconButton(
                    icon: const Icon(Icons.send),
                    onPressed: _handleSend,
                    tooltip: '发送',
                  ),
              ],
            ),
          ),
          
          // 更多功能面板
          if (_showMoreOptions)
            Container(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildOptionButton(
                    icon: Icons.image,
                    label: '图片',
                    onTap: widget.onSendImage,
                  ),
                  _buildOptionButton(
                    icon: Icons.camera_alt,
                    label: '拍照',
                    onTap: widget.onSendImage,
                  ),
                  _buildOptionButton(
                    icon: Icons.file_copy,
                    label: '文件',
                    onTap: widget.onSendFile,
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildVoiceButton() {
    return GestureDetector(
      onLongPressStart: (_) {
        widget.onStartVoice();
      },
      onLongPressEnd: (_) {
        widget.onStopVoice();
      },
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

  Widget _buildOptionButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: Colors.grey[200],
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon),
          ),
          const SizedBox(height: 4),
          Text(label, style: const TextStyle(fontSize: 12)),
        ],
      ),
    );
  }
}
