import 'package:flutter/material.dart';
import '../../../core/routes/route_paths.dart';

class TreasureQuestPage extends StatelessWidget {
  const TreasureQuestPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // 游戏标题栏
          SliverAppBar(
            expandedHeight: 200,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              title: const Text('老克寻宝记'),
              background: Stack(
                fit: StackFit.expand,
                children: [
                  Image.asset(
                    'assets/images/games/treasure_quest_banner.jpg',
                    fit: BoxFit.cover,
                  ),
                  Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Colors.transparent,
                          Colors.black.withOpacity(0.7),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // 主要内容
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 玩家状态卡片
                  _buildPlayerStatusCard(context),
                  const SizedBox(height: 24),

                  // 主要功能按钮
                  _buildMainActions(context),
                  const SizedBox(height: 24),

                  // 每日任务
                  _buildDailyQuests(context),
                  const SizedBox(height: 24),

                  // 最近发现
                  _buildRecentDiscoveries(context),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPlayerStatusCard(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 30,
                  backgroundImage: AssetImage('assets/images/avatar.jpg'),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '探险家等级 7',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: 4),
                      LinearProgressIndicator(
                        value: 0.7,
                        backgroundColor: Colors.grey[200],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '距离下一级还需要300经验',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatusItem(
                  context,
                  icon: Icons.star,
                  label: '成就点数',
                  value: '1,234',
                ),
                _buildStatusItem(
                  context,
                  icon: Icons.inventory_2,
                  label: '收藏品',
                  value: '45/100',
                ),
                _buildStatusItem(
                  context,
                  icon: Icons.place,
                  label: '探索地点',
                  value: '23',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusItem(
    BuildContext context, {
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Column(
      children: [
        Icon(icon, color: Theme.of(context).primaryColor),
        const SizedBox(height: 4),
        Text(
          value,
          style: Theme.of(context).textTheme.titleMedium,
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }

  Widget _buildMainActions(BuildContext context) {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      mainAxisSpacing: 16,
      crossAxisSpacing: 16,
      children: [
        _buildActionCard(
          context,
          title: '开始探索',
          icon: Icons.explore,
          color: Colors.blue,
          onTap: () => Navigator.pushNamed(context, RoutePaths.gameExplore),
        ),
        _buildActionCard(
          context,
          title: '我的背包',
          icon: Icons.inventory_2,
          color: Colors.orange,
          onTap: () => Navigator.pushNamed(context, RoutePaths.gameInventory),
        ),
        _buildActionCard(
          context,
          title: '成就殿堂',
          icon: Icons.emoji_events,
          color: Colors.purple,
          onTap: () => Navigator.pushNamed(context, RoutePaths.gameAchievements),
        ),
        _buildActionCard(
          context,
          title: '排行榜',
          icon: Icons.leaderboard,
          color: Colors.green,
          onTap: () => Navigator.pushNamed(context, RoutePaths.gameLeaderboard),
        ),
      ],
    );
  }

  Widget _buildActionCard(
    BuildContext context, {
    required String title,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                color.withOpacity(0.8),
                color,
              ],
            ),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 48,
                color: Colors.white,
              ),
              const SizedBox(height: 8),
              Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDailyQuests(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '每日任务',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 16),
        Card(
          child: Column(
            children: [
              _buildQuestItem(
                context,
                title: '探索3个新地点',
                progress: 1,
                total: 3,
                reward: '100经验',
              ),
              const Divider(),
              _buildQuestItem(
                context,
                title: '收集5件普通物品',
                progress: 3,
                total: 5,
                reward: '50经验',
              ),
              const Divider(),
              _buildQuestItem(
                context,
                title: '完成1次寻宝挑战',
                progress: 0,
                total: 1,
                reward: '200经验',
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildQuestItem(
    BuildContext context, {
    required String title,
    required int progress,
    required int total,
    required String reward,
  }) {
    final completed = progress >= total;
    return ListTile(
      title: Text(title),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 4),
          LinearProgressIndicator(
            value: progress / total,
            backgroundColor: Colors.grey[200],
          ),
          const SizedBox(height: 4),
          Text('进度: $progress/$total'),
        ],
      ),
      trailing: completed
          ? const Icon(Icons.check_circle, color: Colors.green)
          : Text(
              reward,
              style: TextStyle(color: Theme.of(context).primaryColor),
            ),
    );
  }

  Widget _buildRecentDiscoveries(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '最近发现',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 16),
        SizedBox(
          height: 200,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: 5,
            itemBuilder: (context, index) {
              return Card(
                clipBehavior: Clip.antiAlias,
                child: SizedBox(
                  width: 160,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Image.asset(
                        'assets/images/games/discoveries/item_$index.jpg',
                        height: 100,
                        width: double.infinity,
                        fit: BoxFit.cover,
                      ),
                      Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '神秘物品 #$index',
                              style: Theme.of(context).textTheme.titleSmall,
                            ),
                            const SizedBox(height: 4),
                            Text(
                              '发现于: 昆明市五华区',
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                            const SizedBox(height: 4),
                            Text(
                              '稀有度: ★★★☆☆',
                              style: TextStyle(
                                color: Colors.orange,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
} 