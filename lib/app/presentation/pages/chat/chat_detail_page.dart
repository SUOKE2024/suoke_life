import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/chat_detail_controller.dart';
import '../../widgets/chat/message_list.dart';
import '../../widgets/chat/message_input.dart';
import '../../widgets/chat/chat_app_bar.dart';

class ChatDetailPage extends BasePage<ChatDetailController> {
  const ChatDetailPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return ChatAppBar(
      title: Obx(() => Text(controller.chat.value?.name ?? '')),
      onAvatarTap: controller.showUserProfile,
      onMoreTap: controller.showChatOptions,
      actions: [
        // 语音通话
        IconButton(
          icon: const Icon(Icons.phone),
          onPressed: controller.startVoiceCall,
        ),
        // 视频通话
        IconButton(
          icon: const Icon(Icons.videocam),
          onPressed: controller.startVideoCall,
        ),
      ],
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return Column(
      children: [
        // 消息列表
        Expanded(
          child: MessageList(
            messages: controller.messages,
            onLoadMore: controller.loadMoreMessages,
            onMessageTap: controller.onMessageTap,
            onMessageLongPress: controller.showMessageOptions,
          ),
        ),

        // 输入区域
        MessageInput(
          controller: controller.inputController,
          onSendText: controller.sendTextMessage,
          onSendVoice: controller.sendVoiceMessage,
          onSendImage: controller.sendImageMessage,
          onSendFile: controller.sendFileMessage,
        ),
      ],
    );
  }
} 