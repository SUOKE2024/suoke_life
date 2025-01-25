import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import '../base/base_page.dart';

@RoutePage()
class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return BasePage(
      title: '首页',
      body: ListView(
        children: [
          _buildChatList(),
          _buildRecentServices(),
        ],
      ),
    );
  }

  Widget _buildChatList() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.all(16),
          child: Text('AI助手', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        ),
        SizedBox(
          height: 100,
          child: ListView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            children: [
              _buildAssistantCard('小艾', 'assets/images/assistant_1.png'),
              _buildAssistantCard('老克', 'assets/images/assistant_2.png'),
              _buildAssistantCard('小克', 'assets/images/assistant_3.png'),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildAssistantCard(String name, String image) {
    return Card(
      child: InkWell(
        onTap: () => context.router.pushNamed('/chat/$name'),
        child: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Column(
            children: [
              CircleAvatar(child: Text(name[0])),
              const SizedBox(height: 4),
              Text(name),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRecentServices() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: const [
        Padding(
          padding: EdgeInsets.all(16),
          child: Text('最近使用', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        ),
        // TODO: 实现最近使用的服务列表
      ],
    );
  }
} 