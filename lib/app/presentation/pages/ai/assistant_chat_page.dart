import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../data/models/chat_conversation.dart';
import '../../controllers/chat_detail_controller.dart';
import '../../widgets/chat/chat_message_list.dart';

class AssistantChatPage extends StatelessWidget {
  final ChatConversation conversation;
  
  const AssistantChatPage({
    Key? key,
    required this.conversation,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(ChatDetailController());
    final textController = TextEditingController();

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            CircleAvatar(
              backgroundImage: AssetImage(conversation.avatar),
            ),
            const SizedBox(width: 8),
            Text(conversation.title),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: controller.showSettings,
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Obx(() => ChatMessageList(
              messages: controller.messages,
              onLongPress: controller.onLongPressMessage,
              onTapAvatar: controller.onTapAvatar,
            )),
          ),
          _buildInputArea(controller, textController),
        ],
      ),
    );
  }

  Widget _buildInputArea(ChatDetailController controller, TextEditingController textController) {
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
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: textController,
              decoration: const InputDecoration(
                hintText: '输入消息...',
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              ),
              maxLines: null,
            ),
          ),
          const SizedBox(width: 8),
          Obx(() => controller.isTyping.value
            ? const CircularProgressIndicator()
            : IconButton(
                icon: const Icon(Icons.send),
                onPressed: () {
                  if (textController.text.isNotEmpty) {
                    controller.sendMessage(textController.text);
                    textController.clear();
                  }
                },
              ),
          ),
        ],
      ),
    );
  }
} 