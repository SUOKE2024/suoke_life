import 'package:flutter/material.dart';
import 'package:suoke_life/core/config/app_config.dart';
import 'package:suoke_life/features/home/widgets/health_status_card.dart';
import 'package:suoke_life/features/home/widgets/quick_action_grid.dart';
import 'package:suoke_life/features/home/widgets/notification_indicator.dart';
import 'package:suoke_life/features/home/widgets/recent_activities_section.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(AppConfig.appName),
        actions: const [
          NotificationIndicator(key: Key('notification_indicator'))
        ],
      ),
      body: Column(
        children: [
          // 顶部导航栏
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              IconButton(
                icon: const Icon(Icons.person),
                onPressed: () {
                  // TODO: 用户信息逻辑
                },
              ),
              IconButton(
                icon: const Icon(Icons.add),
                onPressed: () {
                  // TODO: 添加功能逻辑
                },
              ),
            ],
          ),
          // 聊天列表
          Expanded(
            child: ListView.builder(
              itemCount: 10, // 示例数据
              itemBuilder: (context, index) {
                return ListTile(
                  leading: const CircleAvatar(
                    backgroundImage: AssetImage('assets/images/avatar.png'),
                  ),
                  title: Text('联系人 $index'),
                  subtitle: const Text('最新消息预览'),
                  trailing: const Text('时间戳'),
                  onTap: () {
                    // TODO: 聊天界面逻辑
                  },
                );
              },
            ),
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: '首页',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.explore),
            label: '探索',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: '我的',
          ),
        ],
        currentIndex: 0,
        onTap: (index) {
          // TODO: 底部导航逻辑
        },
      ),
    );
  }
}
