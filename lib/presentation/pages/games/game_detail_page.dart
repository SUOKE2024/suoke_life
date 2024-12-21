import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/game_detail_controller.dart';

class GameDetailPage extends GetView<GameDetailController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('游戏详情'),
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return Center(child: CircularProgressIndicator());
        }

        final game = controller.gameDetail.value;
        if (game == null) {
          return Center(child: Text('游戏信息不存在'));
        }

        return SingleChildScrollView(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 游戏封面
              AspectRatio(
                aspectRatio: 16 / 9,
                child: Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(12),
                    image: DecorationImage(
                      image: NetworkImage(game.coverUrl),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
              ),
              SizedBox(height: 16),
              
              // 游戏信息
              Text(
                game.name,
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              SizedBox(height: 8),
              Text(
                game.description,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              SizedBox(height: 16),
              
              // 游戏统计
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildStatItem(
                    icon: Icons.people,
                    label: '玩家数',
                    value: '${game.playerCount}',
                  ),
                  _buildStatItem(
                    icon: Icons.star,
                    label: '评分',
                    value: game.rating.toStringAsFixed(1),
                  ),
                  _buildStatItem(
                    icon: Icons.timer,
                    label: '时长',
                    value: '${game.averagePlayTime}分钟',
                  ),
                ],
              ),
              SizedBox(height: 24),
              
              // 开始游戏按钮
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: controller.startGame,
                  child: Text('开始游戏'),
                  style: ElevatedButton.styleFrom(
                    padding: EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
            ],
          ),
        );
      }),
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Column(
      children: [
        Icon(icon),
        SizedBox(height: 4),
        Text(label),
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
} 