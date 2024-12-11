import 'package:flutter/material.dart';
import '../models/player.dart';
import '../services/game_service.dart';

class AchievementsScreen extends StatefulWidget {
  final Player player;
  final GameService gameService;

  const AchievementsScreen({
    Key? key,
    required this.player,
    required this.gameService,
  }) : super(key: key);

  @override
  State<AchievementsScreen> createState() => _AchievementsScreenState();
}

class _AchievementsScreenState extends State<AchievementsScreen> {
  // 成就分类
  final List<String> _categories = [
    '探索成就',
    '收集成就',
    '社交成就',
    '季节成就',
  ];

  // 成就数据
  final Map<String, List<Achievement>> _achievements = {
    '探索成就': [
      Achievement(
        id: 'first_treasure',
        name: '初次发现',
        description: '发现你的第一个宝藏',
        icon: Icons.emoji_events,
        progress: 1,
        total: 1,
        rewards: {'experience': 100, 'points': 50},
      ),
      Achievement(
        id: 'treasure_hunter',
        name: '寻宝达人',
        description: '发现100个宝藏',
        icon: Icons.search,
        progress: 0,
        total: 100,
        rewards: {'experience': 1000, 'points': 500},
      ),
      Achievement(
        id: 'long_walker',
        name: '远足专家',
        description: '累计行走100公里',
        icon: Icons.directions_walk,
        progress: 0,
        total: 100,
        rewards: {'experience': 500, 'points': 200},
      ),
    ],
    '收集成就': [
      Achievement(
        id: 'mushroom_collector',
        name: '菌类收藏家',
        description: '收集30种不同的野生菌',
        icon: Icons.eco,
        progress: 0,
        total: 30,
        rewards: {'experience': 800, 'points': 300},
      ),
      Achievement(
        id: 'rare_finder',
        name: '稀有发现者',
        description: '发现10个稀有物品',
        icon: Icons.stars,
        progress: 0,
        total: 10,
        rewards: {'experience': 500, 'points': 200},
      ),
    ],
    '社交成就': [
      Achievement(
        id: 'team_player',
        name: '团队玩家',
        description: '参与20次团队探索',
        icon: Icons.group,
        progress: 0,
        total: 20,
        rewards: {'experience': 600, 'points': 250},
      ),
      Achievement(
        id: 'helpful_explorer',
        name: '热心探险家',
        description: '帮助50位其他玩家',
        icon: Icons.favorite,
        progress: 0,
        total: 50,
        rewards: {'experience': 1000, 'points': 400},
      ),
    ],
    '季节成就': [
      Achievement(
        id: 'spring_explorer',
        name: '春日探险家',
        description: '在春季完成所有每日任务',
        icon: Icons.local_florist,
        progress: 0,
        total: 90,
        rewards: {'experience': 1500, 'points': 600},
      ),
      Achievement(
        id: 'summer_master',
        name: '夏日大师',
        description: '在夏季发现100个宝藏',
        icon: Icons.wb_sunny,
        progress: 0,
        total: 100,
        rewards: {'experience': 2000, 'points': 800},
      ),
    ],
  };

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: _categories.length,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('成就'),
          bottom: TabBar(
            isScrollable: true,
            tabs: _categories.map((category) => Tab(text: category)).toList(),
          ),
        ),
        body: TabBarView(
          children: _categories.map((category) {
            return _buildAchievementList(_achievements[category] ?? []);
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildAchievementList(List<Achievement> achievements) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: achievements.length,
      itemBuilder: (context, index) {
        final achievement = achievements[index];
        return _buildAchievementCard(achievement);
      },
    );
  }

  Widget _buildAchievementCard(Achievement achievement) {
    final progress = achievement.progress / achievement.total;
    final isCompleted = progress >= 1.0;

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: InkWell(
        onTap: () => _showAchievementDetails(achievement),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 标题行
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: isCompleted ? Colors.green : Colors.blue,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      achievement.icon,
                      color: Colors.white,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          achievement.name,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          achievement.description,
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (isCompleted)
                    const Icon(
                      Icons.check_circle,
                      color: Colors.green,
                      size: 24,
                    ),
                ],
              ),

              const SizedBox(height: 16),

              // 进度条
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '进度',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                        ),
                      ),
                      Text(
                        '${achievement.progress}/${achievement.total}',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  LinearProgressIndicator(
                    value: progress,
                    backgroundColor: Colors.grey[200],
                    valueColor: AlwaysStoppedAnimation<Color>(
                      isCompleted ? Colors.green : Colors.blue,
                    ),
                  ),
                ],
              ),

              // 奖励预览
              if (!isCompleted) ...[
                const SizedBox(height: 16),
                Row(
                  children: [
                    const Icon(
                      Icons.card_giftcard,
                      size: 16,
                      color: Colors.amber,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '奖励: ${achievement.rewards['experience']} 经验, ${achievement.rewards['points']} 积分',
                      style: const TextStyle(
                        fontSize: 14,
                        color: Colors.amber,
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  void _showAchievementDetails(Achievement achievement) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.7,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(
            top: Radius.circular(20),
          ),
        ),
        child: Column(
          children: [
            // 顶部拖动条
            Container(
              margin: const EdgeInsets.symmetric(vertical: 8),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),

            // 内容区域
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 成就图标和标题
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.blue,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Icon(
                            achievement.icon,
                            color: Colors.white,
                            size: 32,
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                achievement.name,
                                style: const TextStyle(
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                achievement.description,
                                style: TextStyle(
                                  fontSize: 16,
                                  color: Colors.grey[600],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 24),

                    // 进度详情
                    Text(
                      '完成进度',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey[800],
                      ),
                    ),
                    const SizedBox(height: 12),
                    LinearProgressIndicator(
                      value: achievement.progress / achievement.total,
                      backgroundColor: Colors.grey[200],
                      minHeight: 8,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '${achievement.progress}/${achievement.total}',
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.grey[600],
                      ),
                    ),

                    const SizedBox(height: 24),

                    // 奖励详情
                    Text(
                      '完成奖励',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey[800],
                      ),
                    ),
                    const SizedBox(height: 12),
                    _buildRewardItem(
                      Icons.star,
                      '经验值',
                      '${achievement.rewards['experience']}',
                      Colors.orange,
                    ),
                    const SizedBox(height: 8),
                    _buildRewardItem(
                      Icons.monetization_on,
                      '积分',
                      '${achievement.rewards['points']}',
                      Colors.amber,
                    ),

                    const SizedBox(height: 24),

                    // 完成提示
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.blue.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        children: [
                          const Icon(
                            Icons.lightbulb_outline,
                            color: Colors.blue,
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              _getCompletionTip(achievement),
                              style: const TextStyle(
                                fontSize: 14,
                                color: Colors.blue,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRewardItem(
    IconData icon,
    String label,
    String value,
    Color color,
  ) {
    return Row(
      children: [
        Icon(
          icon,
          size: 20,
          color: color,
        ),
        const SizedBox(width: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 16,
            color: Colors.grey[600],
          ),
        ),
        const Spacer(),
        Text(
          value,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  String _getCompletionTip(Achievement achievement) {
    final remaining = achievement.total - achievement.progress;
    if (remaining <= 0) {
      return '恭喜你已经完成了这个成就！';
    }

    switch (achievement.id) {
      case 'first_treasure':
        return '去发现你的第一个宝藏吧！';
      case 'treasure_hunter':
        return '还需要发现 $remaining 个宝藏';
      case 'long_walker':
        return '继续探索，还需要行走 $remaining 公里';
      case 'mushroom_collector':
        return '继续收集不同种类的野生菌，还差 $remaining 种';
      case 'rare_finder':
        return '寻找稀有物品，还需要 $remaining 个';
      case 'team_player':
        return '多参与团队探索，还需要 $remaining 次';
      case 'helpful_explorer':
        return '继续帮助其他玩家，还需要帮助 $remaining 人';
      case 'spring_explorer':
        return '春季每日任务完成进度：${achievement.progress}/$remaining';
      case 'summer_master':
        return '夏季寻宝进度：${achievement.progress}/$remaining';
      default:
        return '继续努力，距离完成还差 $remaining 点进度';
    }
  }
}

class Achievement {
  final String id;
  final String name;
  final String description;
  final IconData icon;
  final int progress;
  final int total;
  final Map<String, int> rewards;

  Achievement({
    required this.id,
    required this.name,
    required this.description,
    required this.icon,
    required this.progress,
    required this.total,
    required this.rewards,
  });
} 