import 'package:flutter/material.dart';
import 'package:get/get.dart';

class ChatInput extends StatefulWidget {
  final Function(String) onSendText;
  final Function(String) onSendVoice;
  final Function(String) onSendImage;
  final Function(String) onSendVideo;

  const ChatInput({
    Key? key,
    required this.onSendText,
    required this.onSendVoice,
    required this.onSendImage,
    required this.onSendVideo,
  }) : super(key: key);

  @override
  State<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends State<ChatInput> {
  final textController = TextEditingController();
  bool isVoiceMode = false;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(8),
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
            IconButton(
              icon: Icon(isVoiceMode ? Icons.keyboard : Icons.mic),
              onPressed: () {
                setState(() {
                  isVoiceMode = !isVoiceMode;
                });
              },
            ),
            if (isVoiceMode)
              Expanded(
                child: GestureDetector(
                  onLongPressStart: (_) {
                    // 开始录音
                  },
                  onLongPressEnd: (_) {
                    // 结束录音并发送
                  },
                  child: Container(
                    height: 36,
                    decoration: BoxDecoration(
                      color: Colors.grey[200],
                      borderRadius: BorderRadius.circular(18),
                    ),
                    alignment: Alignment.center,
                    child: const Text('按住说话'),
                  ),
                ),
              )
            else
              Expanded(
                child: TextField(
                  controller: textController,
                  decoration: InputDecoration(
                    hintText: '输入消息...',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(18),
                      borderSide: BorderSide.none,
                    ),
                    filled: true,
                    fillColor: Colors.grey[200],
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 8,
                    ),
                  ),
                ),
              ),
            IconButton(
              icon: const Icon(Icons.image),
              onPressed: () async {
                final result = await Get.bottomSheet(
                  Container(
                    color: Colors.white,
                    child: SafeArea(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          ListTile(
                            leading: const Icon(Icons.photo_library),
                            title: const Text('相册'),
                            onTap: () => Get.back(result: 'gallery'),
                          ),
                          ListTile(
                            leading: const Icon(Icons.camera_alt),
                            title: const Text('拍照'),
                            onTap: () => Get.back(result: 'camera'),
                          ),
                          ListTile(
                            leading: const Icon(Icons.videocam),
                            title: const Text('视频'),
                            onTap: () => Get.back(result: 'video'),
                          ),
                        ],
                      ),
                    ),
                  ),
                );

                if (result != null) {
                  switch (result) {
                    case 'gallery':
                      // 从相册选择
                      break;
                    case 'camera':
                      // 拍照
                      break;
                    case 'video':
                      // 录制视频
                      break;
                  }
                }
              },
            ),
            IconButton(
              icon: const Icon(Icons.send),
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
      ),
    );
  }

  @override
  void dispose() {
    textController.dispose();
    super.dispose();
  }
} 