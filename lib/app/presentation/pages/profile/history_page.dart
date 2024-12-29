import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/profile/history_controller.dart';

class HistoryPage extends GetView<HistoryController> {
  const HistoryPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('历史记录'),
          bottom: const TabBar(
            tabs: [
              Tab(text: '聊天'),
              Tab(text: '服务'),
              Tab(text: '探索'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _buildChatHistory(),
            _buildServiceHistory(),
            _buildExploreHistory(),
          ],
        ),
      ),
    );
  }

  Widget _buildChatHistory() {
    return Obx(() {
      if (controller.isLoadingChat.value) {
        return const Center(child: CircularProgressIndicator());
      }

      return ListView.builder(
        itemCount: controller.chatHistory.length,
        itemBuilder: (context, index) {
          final chat = controller.chatHistory[index];
          return ListTile(
            leading: CircleAvatar(
              child: Text(chat.title[0].toUpperCase()),
            ),
            title: Text(chat.title),
            subtitle: Text(chat.lastMessage),
            trailing: Text(chat.time),
            onTap: () => controller.openChat(chat),
          );
        },
      );
    });
  }

  Widget _buildServiceHistory() {
    return Obx(() {
      if (controller.isLoadingService.value) {
        return const Center(child: CircularProgressIndicator());
      }

      return ListView.builder(
        itemCount: controller.serviceHistory.length,
        itemBuilder: (context, index) {
          final service = controller.serviceHistory[index];
          return ListTile(
            leading: Icon(service.icon),
            title: Text(service.name),
            subtitle: Text(service.time),
            trailing: Text(service.status),
            onTap: () => controller.openService(service),
          );
        },
      );
    });
  }

  Widget _buildExploreHistory() {
    return Obx(() {
      if (controller.isLoadingExplore.value) {
        return const Center(child: CircularProgressIndicator());
      }

      return ListView.builder(
        itemCount: controller.exploreHistory.length,
        itemBuilder: (context, index) {
          final explore = controller.exploreHistory[index];
          return ListTile(
            leading: explore.imageUrl != null
                ? Image.network(
                    explore.imageUrl!,
                    width: 40,
                    height: 40,
                    fit: BoxFit.cover,
                  )
                : const Icon(Icons.explore),
            title: Text(explore.title),
            subtitle: Text(explore.time),
            onTap: () => controller.openExplore(explore),
          );
        },
      );
    });
  }
} 