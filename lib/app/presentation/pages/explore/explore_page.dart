import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import '../base/base_page.dart';

@RoutePage()
class ExplorePage extends StatelessWidget {
  const ExplorePage({super.key});

  @override
  Widget build(BuildContext context) {
    return BasePage(
      title: '探索',
      body: ListView(
        children: [
          _buildSearchBar(),
          _buildKnowledgeGraph(),
          _buildTopics(),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // TODO: 打开老克助手
        },
        child: const Icon(Icons.chat_bubble),
      ),
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: TextField(
        decoration: InputDecoration(
          hintText: '搜索知识...',
          prefixIcon: const Icon(Icons.search),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(30),
          ),
        ),
      ),
    );
  }

  Widget _buildKnowledgeGraph() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: const [
        Padding(
          padding: EdgeInsets.all(16),
          child: Text('知识图谱', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        ),
        // TODO: 实现知识图谱展示
      ],
    );
  }

  Widget _buildTopics() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: const [
        Padding(
          padding: EdgeInsets.all(16),
          child: Text('热门话题', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        ),
        // TODO: 实现话题列表
      ],
    );
  }
} 