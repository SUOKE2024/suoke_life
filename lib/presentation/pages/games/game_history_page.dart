import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/game_history_controller.dart';

class GameHistoryPage extends GetView<GameHistoryController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('游戏记录'),
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return Center(child: CircularProgressIndicator());
        }

        if (controller.history.isEmpty) {
          return Center(
            child: Text(
              '暂无游戏记录',
              style: TextStyle(color: Colors.grey),
            ),
          );
        }

        return ListView.builder(
          itemCount: controller.history.length,
          itemBuilder: (context, index) {
            final record = controller.history[index];
            return Card(
              margin: EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 8,
              ),
              child: ListTile(
                title: Text(record.gameName),
                subtitle: Text(record.playTime),
                trailing: Text(
                  '得分: ${record.score}',
                  style: TextStyle(
                    color: Theme.of(context).primaryColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            );
          },
        );
      }),
    );
  }
} 