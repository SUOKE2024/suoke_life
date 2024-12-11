import 'package:flutter/material.dart';
import '../models/player.dart';
import '../services/ar_service.dart';
import '../models/game_config.dart';

class GameHUD extends StatelessWidget {
  final Player player;
  final ARService arService;

  const GameHUD({
    Key? key,
    required this.player,
    required this.arService,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // 顶部状态栏
        Positioned(
          top: MediaQuery.of(context).padding.top,
          left: 0,
          right: 0,
          child: _buildTopBar(),
        ),

        // 右侧工具栏
        Positioned(
          top: MediaQuery.of(context).padding.top + 80,
          right: 16,
          child: _buildToolbar(),
        ),

        // 底部状态栏
        Positioned(
          bottom: 0,
          left: 0,
          right: 0,
          child: _buildBottomBar(),
        ),
      ],
    );
  }

  // 顶部状态栏
  Widget _buildTopBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Colors.black.withOpacity(0.7),
            Colors.black.withOpacity(0.0),
          ],
        ),
      ),
      child: Row(
        children: [
          // 玩家头像
          CircleAvatar(
            radius: 20,
            backgroundImage: player.avatarUrl != null
                ? NetworkImage(player.avatarUrl!)
                : null,
            child: player.avatarUrl == null
                ? const Icon(Icons.person)
                : null,
          ),

          const SizedBox(width: 8),

          // 玩家信息
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  player.nickname,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Row(
                  children: [
                    _buildLevelBadge(),
                    const SizedBox(width: 8),
                    _buildExperienceBar(),
                  ],
                ),
              ],
            ),
          ),

          // 积分显示
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 12,
              vertical: 4,
            ),
            decoration: BoxDecoration(
              color: Colors.amber.withOpacity(0.8),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.stars,
                  color: Colors.white,
                  size: 16,
                ),
                const SizedBox(width: 4),
                Text(
                  '${player.points}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // 等级徽章
  Widget _buildLevelBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 8,
        vertical: 2,
      ),
      decoration: BoxDecoration(
        color: Colors.green.withOpacity(0.8),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        'Lv.${player.level}',
        style: const TextStyle(
          color: Colors.white,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  // 经验条
  Widget _buildExperienceBar() {
    final requiredExp = player.calculateRequiredExp(player.level);
    final progress = player.experience / requiredExp;

    return Expanded(
      child: Stack(
        children: [
          // 背景
          Container(
            height: 4,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.3),
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          // 进度
          FractionallySizedBox(
            widthFactor: progress,
            child: Container(
              height: 4,
              decoration: BoxDecoration(
                color: Colors.green,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // 右侧工具栏
  Widget _buildToolbar() {
    return Column(
      children: [
        _buildToolButton(
          icon: Icons.backpack,
          label: '背包',
          onTap: () => _showInventory(),
        ),
        const SizedBox(height: 16),
        _buildToolButton(
          icon: Icons.emoji_events,
          label: '成就',
          onTap: () => _showAchievements(),
        ),
        const SizedBox(height: 16),
        _buildToolButton(
          icon: Icons.leaderboard,
          label: '排行',
          onTap: () => _showLeaderboard(),
        ),
        const SizedBox(height: 16),
        _buildToolButton(
          icon: Icons.settings,
          label: '设置',
          onTap: () => _showSettings(),
        ),
      ],
    );
  }

  // 工具按钮
  Widget _buildToolButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return Column(
      children: [
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.5),
            borderRadius: BorderRadius.circular(24),
          ),
          child: IconButton(
            icon: Icon(icon),
            color: Colors.white,
            onPressed: onTap,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            color: Colors.white,
            fontSize: 12,
            shadows: [
              Shadow(
                color: Colors.black.withOpacity(0.5),
                blurRadius: 4,
              ),
            ],
          ),
        ),
      ],
    );
  }

  // 底部状态栏
  Widget _buildBottomBar() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.bottomCenter,
          end: Alignment.topCenter,
          colors: [
            Colors.black.withOpacity(0.7),
            Colors.black.withOpacity(0.0),
          ],
        ),
      ),
      child: Row(
        children: [
          // 当前赛季信息
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  GameConfig.currentSeason['name'],
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  GameConfig.currentSeason['theme'],
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.8),
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),

          // 特殊奖励展示
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 12,
              vertical: 8,
            ),
            decoration: BoxDecoration(
              color: Colors.purple.withOpacity(0.8),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.card_giftcard,
                  color: Colors.white,
                  size: 20,
                ),
                const SizedBox(width: 8),
                const Text(
                  '特别奖励',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // 显示背包
  void _showInventory() {
    // TODO: 实现背包界面
  }

  // 显示成就
  void _showAchievements() {
    // TODO: 实现成就界面
  }

  // 显示排行榜
  void _showLeaderboard() {
    // TODO: 实现排行榜界面
  }

  // 显示设置
  void _showSettings() {
    // TODO: 实现设置界面
  }
} 