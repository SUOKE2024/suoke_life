import 'package:flutter/material.dart';

class ProductGrid extends StatelessWidget {
  const ProductGrid({super.key});

  @override
  Widget build(BuildContext context) {
    final List<Product> products = [
      const Product(
        name: '有机养生茶',
        description: '精选配方，调理养生',
        price: 128.00,
        imageUrl: 'assets/images/tea.jpg',
        rating: 4.8,
        salesCount: 1234,
      ),
      const Product(
        name: '助眠香薰精油',
        description: '天然植物精油',
        price: 168.00,
        imageUrl: 'assets/images/oil.jpg',
        rating: 4.7,
        salesCount: 856,
      ),
      const Product(
        name: '瑜伽垫套装',
        description: '环保材质，防滑耐用',
        price: 299.00,
        imageUrl: 'assets/images/yoga.jpg',
        rating: 4.9,
        salesCount: 2345,
      ),
      const Product(
        name: '冥想蒲团',
        description: '舒适支撑，静心修习',
        price: 199.00,
        imageUrl: 'assets/images/cushion.jpg',
        rating: 4.6,
        salesCount: 678,
      ),
      const Product(
        name: '天然蜂蜜',
        description: '纯正蜂蜜，滋养调理',
        price: 158.00,
        imageUrl: 'assets/images/honey.jpg',
        rating: 4.9,
        salesCount: 3456,
      ),
      const Product(
        name: '按摩滚轮',
        description: '放松肌肉，缓解疲劳',
        price: 89.00,
        imageUrl: 'assets/images/roller.jpg',
        rating: 4.7,
        salesCount: 1567,
      ),
    ];

    return SliverGrid(
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        mainAxisSpacing: 16.0,
        crossAxisSpacing: 16.0,
        childAspectRatio: 0.75,
      ),
      delegate: SliverChildBuilderDelegate(
        (context, index) {
          final product = products[index];
          return Card(
            clipBehavior: Clip.antiAlias,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  flex: 3,
                  child: Stack(
                    children: [
                      Image.asset(
                        product.imageUrl,
                        width: double.infinity,
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) {
                          return Container(
                            color: Colors.grey[200],
                            child: const Icon(
                              Icons.image,
                              size: 40,
                              color: Colors.grey,
                            ),
                          );
                        },
                      ),
                      Positioned(
                        right: 8,
                        top: 8,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.black.withOpacity(0.6),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Row(
                            children: [
                              const Icon(
                                Icons.star,
                                size: 16,
                                color: Colors.amber,
                              ),
                              const SizedBox(width: 4),
                              Text(
                                product.rating.toString(),
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          product.name,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          product.description,
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Text(
                              '¥${product.price.toStringAsFixed(2)}',
                              style: TextStyle(
                                color: Theme.of(context).primaryColor,
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                            const Spacer(),
                            Text(
                              '${product.salesCount}人付款',
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
        },
        childCount: products.length,
      ),
    );
  }
}

class Product {
  final String name;
  final String description;
  final double price;
  final String imageUrl;
  final double rating;
  final int salesCount;

  const Product({
    required this.name,
    required this.description,
    required this.price,
    required this.imageUrl,
    required this.rating,
    required this.salesCount,
  });
} 