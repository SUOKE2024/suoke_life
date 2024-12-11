import 'package:flutter/material.dart';

class ProductDetailPage extends StatefulWidget {
  const ProductDetailPage({super.key});

  @override
  State<ProductDetailPage> createState() => _ProductDetailPageState();
}

class _ProductDetailPageState extends State<ProductDetailPage> {
  int _currentImageIndex = 0;
  int _quantity = 1;
  String? _selectedSpec;
  bool _isAddingToCart = false;

  final List<String> _productImages = [
    'assets/images/product1.jpg',
    'assets/images/product2.jpg',
    'assets/images/product3.jpg',
  ];

  final List<String> _specifications = [
    '500g/盒',
    '1kg/盒',
    '2kg/盒',
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          CustomScrollView(
            slivers: [
              // 产品图片轮播
              SliverAppBar(
                expandedHeight: 300,
                pinned: true,
                flexibleSpace: FlexibleSpaceBar(
                  background: Stack(
                    children: [
                      PageView.builder(
                        itemCount: _productImages.length,
                        onPageChanged: (index) {
                          setState(() {
                            _currentImageIndex = index;
                          });
                        },
                        itemBuilder: (context, index) {
                          return Image.asset(
                            _productImages[index],
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return Container(
                                color: Colors.grey[200],
                                child: const Icon(
                                  Icons.image,
                                  size: 50,
                                  color: Colors.grey,
                                ),
                              );
                            },
                          );
                        },
                      ),
                      // 图片指示器
                      Positioned(
                        bottom: 16,
                        right: 16,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.black54,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            '${_currentImageIndex + 1}/${_productImages.length}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // 产品信息
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  '有机养生茶',
                                  style: TextStyle(
                                    fontSize: 20,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  '精选配方，调理养生',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey[600],
                                  ),
                                ),
                              ],
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.share),
                            onPressed: () {
                              // TODO: 实现分享功能
                            },
                          ),
                          IconButton(
                            icon: const Icon(Icons.favorite_border),
                            onPressed: () {
                              // TODO: 实现收藏功能
                            },
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          const Text(
                            '¥128.00',
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: Colors.red,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            '¥168.00',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey[600],
                              decoration: TextDecoration.lineThrough,
                            ),
                          ),
                          const Spacer(),
                          Text(
                            '已售 1234',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),

              // 规格选择
              SliverToBoxAdapter(
                child: Container(
                  margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(8),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.05),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        '规格',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: _specifications.map((spec) {
                          final isSelected = _selectedSpec == spec;
                          return ChoiceChip(
                            label: Text(spec),
                            selected: isSelected,
                            onSelected: (selected) {
                              setState(() {
                                _selectedSpec = selected ? spec : null;
                              });
                            },
                          );
                        }).toList(),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          const Text(
                            '数量',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const Spacer(),
                          IconButton(
                            icon: const Icon(Icons.remove),
                            onPressed: _quantity > 1
                                ? () {
                                    setState(() {
                                      _quantity--;
                                    });
                                  }
                                : null,
                          ),
                          Text(
                            _quantity.toString(),
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.add),
                            onPressed: () {
                              setState(() {
                                _quantity++;
                              });
                            },
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),

              // 商品详情
              const SliverToBoxAdapter(
                child: Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '商品详情',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 16),
                      Text(
                        '''
• 产品特点：
  - 精选有机茶叶
  - 传统工艺制作
  - 营养价值丰富

• 功效：
  - 清热解火
  - 养生保健
  - 提神醒脑

• 使用方法：
  - 取3-5克茶叶
  - 95度水温冲泡
  - 浸泡3-5分钟即可饮用

• 储存方法：
  - 避免阳光直射
  - 存放于阴凉干燥处
  - 密封保存
''',
                        style: TextStyle(
                          fontSize: 14,
                          height: 1.6,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // 底部占位
              const SliverToBoxAdapter(
                child: SizedBox(height: 80),
              ),
            ],
          ),

          // 底部购买栏
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 8,
                    offset: const Offset(0, -2),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Expanded(
                    child: FilledButton.tonal(
                      onPressed: () async {
                        if (_selectedSpec == null) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('请选择规格')),
                          );
                          return;
                        }
                        setState(() {
                          _isAddingToCart = true;
                        });
                        // TODO: 实现加入购物车功能
                        await Future.delayed(const Duration(seconds: 1));
                        setState(() {
                          _isAddingToCart = false;
                        });
                        if (mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('已加入购物车')),
                          );
                        }
                      },
                      child: _isAddingToCart
                          ? const SizedBox(
                              width: 24,
                              height: 24,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                              ),
                            )
                          : const Text('加入购物车'),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: FilledButton(
                      onPressed: () {
                        if (_selectedSpec == null) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('请选择规格')),
                          );
                          return;
                        }
                        // TODO: 实现立即购买功能
                      },
                      child: const Text('立即购买'),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
} 