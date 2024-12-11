import 'package:flutter/material.dart';

class ServiceCategoryList extends StatelessWidget {
  const ServiceCategoryList({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 16.0),
          child: Text(
            '全部服务',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        const SizedBox(height: 16),
        Expanded(
          child: ListView(
            children: const [
              ServiceCategoryItem(
                icon: Icons.self_improvement,
                title: '身心平衡',
                subtitle: '冥想练习、呼吸训练、正念减压等',
                color: Colors.blue,
              ),
              ServiceCategoryItem(
                icon: Icons.fitness_center,
                title: '运动健身',
                subtitle: '运动计划、健身指导、体态改善等',
                color: Colors.teal,
              ),
              ServiceCategoryItem(
                icon: Icons.restaurant_menu,
                title: '营养健康',
                subtitle: '膳食指导、营养搭配、健康食谱等',
                color: Colors.indigo,
              ),
              ServiceCategoryItem(
                icon: Icons.nightlight_round,
                title: '睡眠管理',
                subtitle: '睡眠监测、作息调整、助眠指导等',
                color: Colors.purple,
              ),
              ServiceCategoryItem(
                icon: Icons.spa,
                title: '养生保健',
                subtitle: '中医养生、穴位按摩、季节调理等',
                color: Colors.orange,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class ServiceCategoryItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Color color;

  const ServiceCategoryItem({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(
          icon,
          color: color,
        ),
      ),
      title: Text(
        title,
        style: const TextStyle(
          fontWeight: FontWeight.w500,
        ),
      ),
      subtitle: Text(
        subtitle,
        style: TextStyle(
          color: Colors.grey[600],
          fontSize: 12,
        ),
      ),
      trailing: const Icon(Icons.chevron_right),
      onTap: () {
        // TODO: 处理分类点击事件
      },
    );
  }
} 