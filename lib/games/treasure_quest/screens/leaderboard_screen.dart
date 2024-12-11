import 'package:flutter/material.dart';
import '../models/player.dart';
import '../services/game_service.dart';

class LeaderboardScreen extends StatefulWidget {
  final Player player;
  final GameService gameService;

  const LeaderboardScreen({
    Key? key,
    required this.player,
    required this.gameService,
  }) : super(key: key);

  @override
  State<LeaderboardScreen> createState() => _LeaderboardScreenState();
}

class _LeaderboardScreenState extends State<LeaderboardScreen> {
  final List<String> _categories = [
    '总积分',
    '探索达人',
    '收藏大师',
    '社交之星',
  ];

  // 模拟排行榜数据
  final Map<String, List<LeaderboardEntry>> _leaderboardData = {
    '总积分': [
      LeaderboardEntry(
        rank: 1,
        name: '云游者',
        avatar: 'assets/avatars/1.png',
        score: 12800,
        isCurrentUser: false,
      ),
      LeaderboardEntry(
        rank: 2,
        name: '寻宝客',
        avatar: 'assets/avatars/2.png',
        score: 11500,
        isCurrentUser: false,
      ),
      LeaderboardEntry(
        rank: 3,
        name: '蘑菇达人',
        avatar: 'assets/avatars/3.png',
        score: 10200,
        isCurrentUser: false,
      ),
    ],
    '探索达人': [
      LeaderboardEntry(
        rank: 1,
        name: '远行者',
        avatar: 'assets/avatars/4.png',
        score: 156,
        isCurrentUser: false,
        subtitle: '发现宝藏数',
      ),
      LeaderboardEntry(
        rank: 2,
        name: '探路者',
        avatar: 'assets/avatars/5.png',
        score: 143,
        isCurrentUser: false,
        subtitle: '发现宝藏数',
      ),
      LeaderboardEntry(
        rank: 3,
        name: '寻宝人',
        avatar: 'assets/avatars/6.png',
        score: 128,
        isCurrentUser: false,
        subtitle: '发现宝藏数',
      ),
    ],
    '收藏大师': [
      LeaderboardEntry(
        rank: 1,
        name: '采集者',
        avatar: 'assets/avatars/7.png',
        score: 89,
        isCurrentUser: false,
        subtitle: '收藏品数量',
      ),
      LeaderboardEntry(
        rank: 2,
        name: '收藏家',
        avatar: 'assets/avatars/8.png',
        score: 76,
        isCurrentUser: false,
        subtitle: '收藏品数量',
      ),
      LeaderboardEntry(
        rank: 3,
        name: '鉴赏师',
        avatar: 'assets/avatars/9.png',
        score: 65,
        isCurrentUser: false,
        subtitle: '收藏品数量',
      ),
    ],
    '社交之星': [
      LeaderboardEntry(
        rank: 1,
        name: '交际花',
        avatar: 'assets/avatars/10.png',
        score: 234,
        isCurrentUser: false,
        subtitle: '互动次数',
      ),
      LeaderboardEntry(
        rank: 2,
        name: '热心人',
        avatar: 'assets/avatars/11.png',
        score: 198,
        isCurrentUser: false,
        subtitle: '互动次数',
      ),
      LeaderboardEntry(
        rank: 3,
        name: '引路人',
        avatar: 'assets/avatars/12.png',
        score: 167,
        isCurrentUser: false,
        subtitle: '互动次数',
      ),
    ],
  };

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: _categories.length,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('排行榜'),
          bottom: TabBar(
            isScrollable: true,
            tabs: _categories.map((category) => Tab(text: category)).toList(),
          ),
        ),
        body: TabBarView(
          children: _categories.map((category) {
            return _buildLeaderboardList(_leaderboardData[category] ?? []);
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildLeaderboardList(List<LeaderboardEntry> entries) {
    return Column(
      children: [
        // 顶部三甲展示
        if (entries.length >= 3) _buildTopThree(entries.take(3).toList()),
        
        // 分割线
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 16),
          child: Divider(height: 32),
        ),

        // 完整排行榜
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: entries.length,
            itemBuilder: (context, index) {
              final entry = entries[index];
              return _buildRankListItem(entry);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildTopThree(List<LeaderboardEntry> topThree) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          // 第二名
          if (topThree.length > 1)
            _buildTopThreeItem(
              topThree[1],
              size: 100,
              borderColor: Colors.grey.shade400,
            ),
          
          // 第一名
          _buildTopThreeItem(
            topThree[0],
            size: 120,
            borderColor: Colors.amber,
            showCrown: true,
          ),
          
          // 第三名
          if (topThree.length > 2)
            _buildTopThreeItem(
              topThree[2],
              size: 100,
              borderColor: Colors.brown.shade300,
            ),
        ],
      ),
    );
  }

  Widget _buildTopThreeItem(
    LeaderboardEntry entry, {
    required double size,
    required Color borderColor,
    bool showCrown = false,
  }) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (showCrown)
          const Icon(
            Icons.crown_rounded,
            color: Colors.amber,
            size: 32,
          ),
        Stack(
          alignment: Alignment.center,
          children: [
            Container(
              width: size,
              height: size,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: borderColor,
                  width: 4,
                ),
              ),
              child: ClipOval(
                child: Image.asset(
                  entry.avatar,
                  fit: BoxFit.cover,
                ),
              ),
            ),
            Positioned(
              bottom: 0,
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 8,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: borderColor,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${entry.score}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          entry.name,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),
        if (entry.subtitle != null)
          Text(
            entry.subtitle!,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
      ],
    );
  }

  Widget _buildRankListItem(LeaderboardEntry entry) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: entry.isCurrentUser ? Colors.blue.withOpacity(0.1) : null,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Colors.grey.withOpacity(0.2),
        ),
      ),
      child: Row(
        children: [
          // 排名
          Container(
            width: 32,
            height: 32,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: _getRankBgColor(entry.rank),
              shape: BoxShape.circle,
            ),
            child: Text(
              '${entry.rank}',
              style: TextStyle(
                color: _getRankTextColor(entry.rank),
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(width: 12),

          // 头像
          CircleAvatar(
            radius: 20,
            backgroundImage: AssetImage(entry.avatar),
          ),
          const SizedBox(width: 12),

          // 用户信息
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  entry.name,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (entry.subtitle != null)
                  Text(
                    entry.subtitle!,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
              ],
            ),
          ),

          // 分数
          Text(
            '${entry.score}',
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Color _getRankBgColor(int rank) {
    switch (rank) {
      case 1:
        return Colors.amber;
      case 2:
        return Colors.grey.shade400;
      case 3:
        return Colors.brown.shade300;
      default:
        return Colors.grey.shade200;
    }
  }

  Color _getRankTextColor(int rank) {
    switch (rank) {
      case 1:
      case 2:
      case 3:
        return Colors.white;
      default:
        return Colors.grey.shade700;
    }
  }
}

class LeaderboardEntry {
  final int rank;
  final String name;
  final String avatar;
  final int score;
  final bool isCurrentUser;
  final String? subtitle;

  LeaderboardEntry({
    required this.rank,
    required this.name,
    required this.avatar,
    required this.score,
    required this.isCurrentUser,
    this.subtitle,
  });
} 