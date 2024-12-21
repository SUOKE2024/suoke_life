import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/games_controller.dart';
import 'package:suoke_life/routes/app_routes.dart';

class GamesPage extends GetView<GamesController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Obx(() => Text(controller.title)),
      ),
      body: GridView.builder(
        padding: EdgeInsets.all(16),
        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
        ),
        itemCount: 6,
        itemBuilder: (context, index) {
          return Card(
            child: InkWell(
              onTap: () => Get.toNamed(
                AppRoutes.GAME_DETAIL,
                arguments: {'gameId': index},
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.games, size: 48),
                  SizedBox(height: 8),
                  Text('游戏 ${index + 1}'),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
} 