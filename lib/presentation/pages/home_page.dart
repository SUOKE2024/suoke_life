import 'package:flutter/material.dart';
import '../widgets/ai_assistant_card.dart';
import '../widgets/feature_grid.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            floating: true,
            title: const Text('索克生活'),
            actions: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined),
                onPressed: () {
                  Navigator.pushNamed(context, '/notifications');
                },
              ),
            ],
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              child: Text(
                'AI助理',
                style: theme.textTheme.titleLarge,
              ),
            ),
          ),
          SliverToBoxAdapter(
            child: Column(
              children: [
                AIAssistantCard(
                  name: '索儿',
                  role: '生活助理',
                  avatar: 'assets/images/soer.png',
                  description: '您的贴心生活小助手',
                  onTap: () {
                    Navigator.pushNamed(context, '/chat/soer');
                  },
                ),
                AIAssistantCard(
                  name: '老克',
                  role: '知识助理',
                  avatar: 'assets/images/claude.png',
                  description: '专业知识解答专家',
                  onTap: () {
                    Navigator.pushNamed(context, '/chat/claude');
                  },
                ),
                AIAssistantCard(
                  name: '小克',
                  role: '商务助理',
                  avatar: 'assets/images/suoke.png',
                  description: '高效的商务好帮手',
                  onTap: () {
                    Navigator.pushNamed(context, '/chat/suoke');
                  },
                ),
              ],
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 24, 16, 8),
              child: Text(
                '常用功能',
                style: theme.textTheme.titleLarge,
              ),
            ),
          ),
          SliverToBoxAdapter(
            child: FeatureGrid(
              items: [
                FeatureItem(
                  title: '健康检测',
                  icon: Icons.health_and_safety,
                  color: Colors.green,
                  onTap: () {
                    Navigator.pushNamed(context, '/health/check');
                  },
                ),
                FeatureItem(
                  title: '智能饮品',
                  icon: Icons.local_drink,
                  color: Colors.blue,
                  onTap: () {
                    Navigator.pushNamed(context, '/drink/order');
                  },
                ),
                FeatureItem(
                  title: '运动计划',
                  icon: Icons.fitness_center,
                  color: Colors.orange,
                  onTap: () {
                    Navigator.pushNamed(context, '/fitness/plan');
                  },
                ),
                FeatureItem(
                  title: '营养方案',
                  icon: Icons.restaurant_menu,
                  color: Colors.purple,
                  onTap: () {
                    Navigator.pushNamed(context, '/nutrition/plan');
                  },
                ),
                FeatureItem(
                  title: '作息管理',
                  icon: Icons.schedule,
                  color: Colors.teal,
                  onTap: () {
                    Navigator.pushNamed(context, '/schedule');
                  },
                ),
                FeatureItem(
                  title: '专家咨询',
                  icon: Icons.people,
                  color: Colors.indigo,
                  onTap: () {
                    Navigator.pushNamed(context, '/expert/consult');
                  },
                ),
                FeatureItem(
                  title: '健康商城',
                  icon: Icons.shopping_cart,
                  color: Colors.red,
                  onTap: () {
                    Navigator.pushNamed(context, '/shop');
                  },
                ),
                FeatureItem(
                  title: '更多服务',
                  icon: Icons.more_horiz,
                  color: Colors.grey,
                  onTap: () {
                    Navigator.pushNamed(context, '/services');
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
} 