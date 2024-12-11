import 'package:flutter/material.dart';

class ProductCarousel extends StatefulWidget {
  const ProductCarousel({super.key});

  @override
  State<ProductCarousel> createState() => _ProductCarouselState();
}

class _ProductCarouselState extends State<ProductCarousel> {
  int _currentPage = 0;
  final List<ProductCarouselItem> _items = [
    const ProductCarouselItem(
      title: '每日养生茶',
      description: '传统配方，调理养生',
      price: 128.00,
      imageUrl: 'assets/images/product1.jpg',
      backgroundColor: Color(0xFFE8F5E9),
    ),
    const ProductCarouselItem(
      title: '助眠香薰精油',
      description: '天然植物精油，改善睡眠',
      price: 168.00,
      imageUrl: 'assets/images/product2.jpg',
      backgroundColor: Color(0xFFE3F2FD),
    ),
    const ProductCarouselItem(
      title: '瑜伽垫套装',
      description: '环保材质，防滑耐用',
      price: 299.00,
      imageUrl: 'assets/images/product3.jpg',
      backgroundColor: Color(0xFFFCE4EC),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SizedBox(
          height: 200,
          child: PageView.builder(
            itemCount: _items.length,
            onPageChanged: (index) {
              setState(() {
                _currentPage = index;
              });
            },
            itemBuilder: (context, index) {
              return Container(
                margin: const EdgeInsets.symmetric(horizontal: 16.0),
                decoration: BoxDecoration(
                  color: _items[index].backgroundColor,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Stack(
                  children: [
                    Positioned(
                      right: 0,
                      bottom: 0,
                      top: 0,
                      child: ClipRRect(
                        borderRadius: const BorderRadius.horizontal(
                          right: Radius.circular(16),
                        ),
                        child: Image.asset(
                          _items[index].imageUrl,
                          width: 160,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) {
                            return Container(
                              width: 160,
                              color: Colors.grey[200],
                              child: const Icon(
                                Icons.image,
                                size: 40,
                                color: Colors.grey,
                              ),
                            );
                          },
                        ),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            _items[index].title,
                            style: const TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            _items[index].description,
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey[600],
                            ),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            '¥${_items[index].price.toStringAsFixed(2)}',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Theme.of(context).primaryColor,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(
            _items.length,
            (index) => Container(
              margin: const EdgeInsets.symmetric(horizontal: 4),
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: _currentPage == index
                    ? Theme.of(context).primaryColor
                    : Colors.grey[300],
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class ProductCarouselItem {
  final String title;
  final String description;
  final double price;
  final String imageUrl;
  final Color backgroundColor;

  const ProductCarouselItem({
    required this.title,
    required this.description,
    required this.price,
    required this.imageUrl,
    required this.backgroundColor,
  });
} 