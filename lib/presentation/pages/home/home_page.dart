import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/home_controller.dart';
import 'package:suoke_life/routes/app_routes.dart';

class HomePage extends GetView<HomeController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('索克生活'),
        actions: [
          // 用户信息按钮(带未读角标)
          Stack(
            children: [
              IconButton(
                icon: Icon(Icons.person_outline),
                onPressed: () => controller.onUserInfoTap(),
              ),
              Positioned(
                right: 8,
                top: 8,
                child: Obx(() => controller.unreadCount.value > 0
                  ? Container(
                      padding: EdgeInsets.all(4),
                      decoration: BoxDecoration(
                        color: Colors.red,
                        shape: BoxShape.circle,
                      ),
                      child: Text(
                        '${controller.unreadCount}',
                        style: TextStyle(color: Colors.white, fontSize: 12),
                      ),
                    )
                  : SizedBox.shrink()),
              ),
            ],
          ),
          // 添加按钮1
          PopupMenuButton(
            icon: Icon(Icons.add_circle_outline),
            itemBuilder: (context) => [
              PopupMenuItem(
                child: Text('添加朋友'),
                value: 'add_friend',
              ),
              PopupMenuItem(
                child: Text('发起群聊'),
                value: 'create_group',
              ),
              PopupMenuItem(
                child: Text('预约咨询'),
                value: 'consultation',
              ),
              PopupMenuItem(
                child: Text('扫一扫'),
                value: 'scan',
              ),
              PopupMenuItem(
                child: Text('收付款'),
                value: 'payment',
              ),
            ],
            onSelected: controller.onMenuSelected,
          ),
          // 添加按钮2 - 会员注册
          IconButton(
            icon: Icon(Icons.card_membership),
            onPressed: () => controller.onMembershipTap(),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Obx(() => ListView.builder(
              itemCount: controller.chatList.length,
              itemBuilder: (context, index) {
                final chat = controller.chatList[index];
                return ListTile(
                  leading: CircleAvatar(
                    backgroundImage: AssetImage(chat.avatar),
                  ),
                  title: Text(chat.name),
                  subtitle: Text(chat.lastMessage),
                  trailing: chat.unreadCount > 0
                    ? Container(
                        padding: EdgeInsets.all(6),
                        decoration: BoxDecoration(
                          color: Colors.red,
                          shape: BoxShape.circle,
                        ),
                        child: Text(
                          '${chat.unreadCount}',
                          style: TextStyle(color: Colors.white, fontSize: 12),
                        ),
                      )
                    : null,
                  onTap: () => controller.onChatTap(chat),
                );
              },
            )),
          ),
          // AI助手悬浮按钮
          Positioned(
            right: 16,
            bottom: 16,
            child: FloatingActionButton(
              child: Icon(Icons.smart_toy),
              onPressed: () => controller.onAIAssistantTap(),
            ),
          ),
        ],
      ),
    );
  }
} 