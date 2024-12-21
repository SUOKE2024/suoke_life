import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/routes/route_paths.dart';

class ExplorePage extends StatelessWidget {
  final List<ExploreItem> channels = [
    ExploreItem(
      title: '知识岛',
      icon: Icons.school,
      page: KnowledgeIslandPage(),
    ),
    ExploreItem(
      title: '咖啡时光',
      icon: Icons.coffee,
      page: CoffeeTimePage(), 
    ),
    ExploreItem(
      title: '美食探店',
      icon: Icons.restaurant,
      page: FoodExplorePage(),
    ),
    // ... 其他探索频道
  ];

  // 右下角老克助手气泡
  Widget buildAIAssistant() => AIAssistantBubble(
    avatar: 'laoke.png',
    onTap: () => Get.to(LaokeAssistantPage()),
  );

  const ExplorePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('探索'),
        actions: [
          IconButton(
            icon: const Icon(Icons.leaderboard_outlined),
            onPressed: () => Get.toNamed(RoutePaths.gameLeaderboard),
          ),
        ],
      ),
      body: Stack(
        children: [
          // 空状态提示
          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.explore,
                  size: 64,
                  color: Colors.grey[400],
                ),
                const SizedBox(height: 16),
                Text(
                  '还没有探索项目',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '点击右下角克图标开始探索',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[500],
                  ),
                ),
              ],
            ),
          ),
          
          // 老克助手
          Positioned(
            right: 16,
            bottom: 16,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                // 提示气泡
                Container(
                  margin: const EdgeInsets.only(right: 8, bottom: 8),
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        '需要我带你去探索吗？',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[800],
                        ),
                      ),
                      const SizedBox(width: 8),
                      Icon(
                        Icons.arrow_downward,
                        size: 16,
                        color: Colors.grey[600],
                      ),
                    ],
                  ),
                ),
                // 老克头像按钮
                FloatingActionButton(
                  onPressed: () => Get.toNamed(RoutePaths.laokeChat),
                  backgroundColor: Colors.white,
                  elevation: 4,
                  child: Stack(
                    children: [
                      const CircleAvatar(
                        radius: 28,
                        backgroundColor: Colors.blue,
                        child: Icon(
                          Icons.psychology,
                          color: Colors.white,
                          size: 32,
                        ),
                      ),
                      Positioned(
                        right: 0,
                        bottom: 0,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                          decoration: BoxDecoration(
                            color: Colors.blue,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Text(
                            'AI',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 8,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
} 