import 'package:flutter/material.dart';
import '../../widgets/product_carousel.dart';
import '../../widgets/product_categories.dart';
import '../../widgets/product_grid.dart';

class ProductPage extends StatelessWidget {
  const ProductPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('健康好物'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.shopping_cart),
            onPressed: () {
              // TODO: 实现购物车功能
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          CustomScrollView(
            slivers: [
              // 搜索栏
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: SearchBar(
                    hintText: '搜索健康好物',
                    leading: const Icon(Icons.search),
                    padding: const MaterialStatePropertyAll(
                      EdgeInsets.symmetric(horizontal: 16.0),
                    ),
                    onTap: () {
                      // TODO: 实现搜索功能
                    },
                  ),
                ),
              ),
              
              // 推荐产品轮播
              const SliverToBoxAdapter(
                child: ProductCarousel(),
              ),

              // 分类列表
              const SliverToBoxAdapter(
                child: Padding(
                  padding: EdgeInsets.only(top: 16.0),
                  child: ProductCategories(),
                ),
              ),

              // 热门商品标题
              const SliverToBoxAdapter(
                child: Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Text(
                    '热门好物',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),

              // 产品网格
              const SliverPadding(
                padding: EdgeInsets.symmetric(horizontal: 16.0),
                sliver: ProductGrid(),
              ),

              // 底部间距
              const SliverToBoxAdapter(
                child: SizedBox(height: 80),
              ),
            ],
          ),
          Positioned(
            right: 16,
            bottom: 16,
            child: FloatingActionButton.extended(
              onPressed: () {
                showModalBottomSheet(
                  context: context,
                  builder: (context) => Container(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Text(
                          '供应商入口',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        ListTile(
                          leading: const Icon(Icons.store),
                          title: const Text('供应商申请'),
                          subtitle: const Text('成为我们的合作伙伴'),
                          onTap: () {
                            Navigator.pop(context);
                            Navigator.pushNamed(context, '/supplier/application');
                          },
                        ),
                        ListTile(
                          leading: const Icon(Icons.add_business),
                          title: const Text('产品录入'),
                          subtitle: const Text('已认证供应商可录入产品'),
                          onTap: () {
                            Navigator.pop(context);
                            Navigator.pushNamed(context, '/supplier/product-entry');
                          },
                        ),
                      ],
                    ),
                  ),
                );
              },
              icon: const Icon(Icons.store),
              label: const Text('供应商入口'),
            ),
          ),
        ],
      ),
    );
  }
} 