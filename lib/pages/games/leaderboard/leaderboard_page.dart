import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'leaderboard_controller.dart';

class LeaderboardPage extends GetView<LeaderboardController> {
  const LeaderboardPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('排行榜'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Get.back(),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: controller.refreshLeaderboard,
        child: Obx(() => controller.isLoading.value
            ? const Center(child: CircularProgressIndicator())
            : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: controller.leaderboardItems.length,
                itemBuilder: (context, index) {
                  final item = controller.leaderboardItems[index];
                  return Card(
                    elevation: 2,
                    margin: const EdgeInsets.only(bottom: 12),
                    child: ListTile(
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 8,
                      ),
                      leading: CircleAvatar(
                        backgroundColor: _getLeaderColor(index),
                        child: Text(
                          '${index + 1}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      title: Text(
                        item.userName,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      trailing: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.blue.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Text(
                          '${item.score}分',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.blue,
                          ),
                        ),
                      ),
                    ),
                  );
                },
              )),
      ),
    );
  }

  Color _getLeaderColor(int index) {
    switch (index) {
      case 0:
        return Colors.amber; // 金牌
      case 1:
        return Colors.grey[400]!; // 银牌
      case 2:
        return Colors.brown; // 铜牌
      default:
        return Colors.blue; // 其他
    }
  }
}
