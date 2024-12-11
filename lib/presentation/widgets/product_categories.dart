import 'package:flutter/material.dart';

class ProductCategories extends StatelessWidget {
  const ProductCategories({super.key});

  @override
  Widget build(BuildContext context) {
    final List<ProductCategory> categories = [
      const ProductCategory(
        icon: Icons.eco,
        label: '优质农产',
        color: Colors.green,
      ),
      const ProductCategory(
        icon: Icons.set_meal,
        label: '预定制品',
        color: Colors.orange,
      ),
      const ProductCategory(
        icon: Icons.spa,
        label: '养生茶饮',
        color: Colors.teal,
      ),
      const ProductCategory(
        icon: Icons.self_improvement,
        label: '冥想助眠',
        color: Colors.blue,
      ),
      const ProductCategory(
        icon: Icons.fitness_center,
        label: '运动装备',
        color: Colors.deepOrange,
      ),
      const ProductCategory(
        icon: Icons.restaurant,
        label: '健康食品',
        color: Colors.red,
      ),
      const ProductCategory(
        icon: Icons.home,
        label: '生活用品',
        color: Colors.purple,
      ),
    ];

    return SizedBox(
      height: 100,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 8.0),
        itemCount: categories.length,
        itemBuilder: (context, index) {
          final category = categories[index];
          return GestureDetector(
            onTap: () {
              // TODO: 导航到分类详情页面
            },
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    width: 60,
                    height: 60,
                    decoration: BoxDecoration(
                      color: category.color.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(30),
                    ),
                    child: Icon(
                      category.icon,
                      color: category.color,
                      size: 30,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    category.label,
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class ProductCategory {
  final IconData icon;
  final String label;
  final Color color;

  const ProductCategory({
    required this.icon,
    required this.label,
    required this.color,
  });
} 