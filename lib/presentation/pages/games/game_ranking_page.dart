import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/game_ranking_controller.dart';

class GameRankingPage extends GetView<GameRankingController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('排行榜'),
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return Center(child: CircularProgressIndicator());
        }

        return ListView.builder(
          itemCount: controller.rankings.length,
          itemBuilder: (context, index) {
            final ranking = controller.rankings[index];
            return ListTile(
              leading: _buildRankBadge(index + 1),
              title: Text(ranking.playerName),
              subtitle: Text(ranking.lastPlayTime),
              trailing: Text(
                ranking.score.toString(),
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Theme.of(context).primaryColor,
                ),
              ),
            );
          },
        );
      }),
    );
  }

  Widget _buildRankBadge(int rank) {
    Color color;
    switch (rank) {
      case 1:
        color = Colors.amber;
        break;
      case 2:
        color = Colors.grey[300]!;
        break;
      case 3:
        color = Colors.brown;
        break;
      default:
        color = Colors.grey[100]!;
    }

    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
      ),
      child: Center(
        child: Text(
          rank.toString(),
          style: TextStyle(
            color: rank <= 3 ? Colors.white : Colors.grey[800],
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
} 