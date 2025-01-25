import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import '../base/base_page.dart';

@RoutePage()
class LifePage extends StatelessWidget {
  const LifePage({super.key});

  @override
  Widget build(BuildContext context) {
    return BasePage(
      title: '生活',
      body: ListView(
        children: [
          _buildHealthStats(),
          _buildDailyRecord(),
          _buildRecommendations(),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // TODO: 打开小克助手
        },
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildHealthStats() {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            Text('健康数据', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 16),
            // TODO: 实现健康数据展示
          ],
        ),
      ),
    );
  }

  Widget _buildDailyRecord() {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            Text('今日记录', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 16),
            // TODO: 实现日常记录展示
          ],
        ),
      ),
    );
  }

  Widget _buildRecommendations() {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            Text('个性化建议', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 16),
            // TODO: 实现建议列表
          ],
        ),
      ),
    );
  }
} 