import 'package:flutter/material.dart';

class AchievementsPage extends StatelessWidget {
  const AchievementsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 4,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('成就殿堂'),
          bottom: const TabBar(
            tabs: [
              Tab(text: '探索'),
              Tab(text: '收藏'),
              Tab(text: '社交'),
              Tab(text: '挑战'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _buildAchievementList(context, _explorationAchievements),
            _buildAchievementList(context, _collectionAchievements),
            _buildAchievementList(context, _socialAchievements),
            _buildAchievementList(context, _challengeAchievements),
          ],
        ),
      ),
    );
  }

  Widget _buildAchievementList(BuildContext context, List<Achievement> achievements) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: achievements.length,
      itemBuilder: (context, index) {
        final achievement = achievements[index];
        return Card(
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: achievement.completed
                  ? Theme.of(context).primaryColor
                  : Colors.grey[300],
              child: Icon(
                achievement.icon,
                color: achievement.completed ? Colors.white : Colors.grey[600],
              ),
            ),
            title: Text(achievement.title),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(achievement.description),
                const SizedBox(height: 8),
                if (achievement.progress != null) ...[
                  LinearProgressIndicator(
                    value: achievement.progress! / achievement.total!,
                    backgroundColor: Colors.grey[200],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '进度: ${achievement.progress}/${achievement.total}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ],
            ),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  achievement.completed
                      ? Icons.check_circle
                      : Icons.check_circle_outline,
                  color: achievement.completed ? Colors.green : Colors.grey,
                ),
                Text(
                  '+${achievement.points}点',
                  style: TextStyle(
                    color: achievement.completed
                        ? Theme.of(context).primaryColor
                        : Colors.grey,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class Achievement {
  final String title;
  final String description;
  final IconData icon;
  final int points;
  final bool completed;
  final int? progress;
  final int? total;

  const Achievement({
    required this.title,
    required this.description,
    required this.icon,
    required this.points,
    this.completed = false,
    this.progress,
    this.total,
  });
}

final List<Achievement> _explorationAchievements = [
  Achievement(
    title: '初出茅庐',
    description: '完成第一次探索',
    icon: Icons.explore,
    points: 10,
    completed: true,
  ),
  Achievement(
    title: '探索达人',
    description: '探索10个不同的地点',
    icon: Icons.place,
    points: 50,
    progress: 7,
    total: 10,
  ),
  Achievement(
    title: '云南走透透',
    description: '探索云南所有主要城市',
    icon: Icons.map,
    points: 100,
    progress: 3,
    total: 16,
  ),
  Achievement(
    title: '登峰造极',
    description: '到达海拔3000米以上的地点',
    icon: Icons.landscape,
    points: 30,
    completed: false,
  ),
];

final List<Achievement> _collectionAchievements = [
  Achievement(
    title: '初级收藏家',
    description: '收集10件不同的物品',
    icon: Icons.collections,
    points: 20,
    progress: 8,
    total: 10,
  ),
  Achievement(
    title: '稀有猎人',
    description: '收集一件传说级别的物品',
    icon: Icons.stars,
    points: 50,
    completed: false,
  ),
  Achievement(
    title: '茶道大师',
    description: '收集所有种类的普洱茶',
    icon: Icons.local_cafe,
    points: 80,
    progress: 4,
    total: 12,
  ),
  Achievement(
    title: '文物专家',
    description: '收集5件历史文物',
    icon: Icons.museum,
    points: 100,
    progress: 2,
    total: 5,
  ),
];

final List<Achievement> _socialAchievements = [
  Achievement(
    title: '社交新手',
    description: '添加第一个好友',
    icon: Icons.person_add,
    points: 10,
    completed: true,
  ),
  Achievement(
    title: '组队达人',
    description: '完成10次组队探索',
    icon: Icons.group,
    points: 50,
    progress: 3,
    total: 10,
  ),
  Achievement(
    title: '分享专家',
    description: '分享50次探索发现',
    icon: Icons.share,
    points: 30,
    progress: 25,
    total: 50,
  ),
  Achievement(
    title: '社区领袖',
    description: '获得100个点赞',
    icon: Icons.thumb_up,
    points: 80,
    progress: 45,
    total: 100,
  ),
];

final List<Achievement> _challengeAchievements = [
  Achievement(
    title: '挑战者',
    description: '完成第一个寻宝挑战',
    icon: Icons.flag,
    points: 20,
    completed: true,
  ),
  Achievement(
    title: '速度之王',
    description: '在10分钟内完成一次寻宝挑战',
    icon: Icons.timer,
    points: 50,
    completed: false,
  ),
  Achievement(
    title: '百战百胜',
    description: '连续完成10次寻宝挑战',
    icon: Icons.military_tech,
    points: 100,
    progress: 4,
    total: 10,
  ),
  Achievement(
    title: '终极挑战',
    description: '完成"寻找失落的茶马古道"终极挑战',
    icon: Icons.emoji_events,
    points: 200,
    completed: false,
  ),
]; 