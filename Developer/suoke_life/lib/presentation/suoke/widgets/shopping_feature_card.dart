import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import '../../../core/router/app_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/animated_gradient_card.dart';
import '../../../core/widgets/animated_press_button.dart';
import '../../../di/providers/shopping_providers.dart';

class ShoppingFeatureCard extends ConsumerWidget {
  const ShoppingFeatureCard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final featuredProducts = ref.watch(featuredProductsProvider);
    final cartItemCount = ref.watch(cartItemCountProvider);
    
    return AnimatedGradientCard(
      title: '索克商城',
      subtitle: '养生好物 助您健康生活',
      gradientColors: [AppColors.secondaryColor, const Color(0xFFB3570A)],
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildPromotionBanner(context),
          
          const SizedBox(height: 16),
          
          const Text(
            '精选好物',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          
          const SizedBox(height: 10),
          
          SizedBox(
            height: 150,
            child: featuredProducts.when(
              data: (products) {
                if (products.isEmpty) {
                  return const Center(
                    child: Text(
                      '暂无精选商品',
                      style: TextStyle(color: Colors.white70),
                    ),
                  );
                }
                
                return ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: products.length > 5 ? 5 : products.length,
                  itemBuilder: (context, index) {
                    final product = products[index];
                    return _buildProductItem(context, product);
                  },
                );
              },
              loading: () => const Center(
                child: CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              ),
              error: (_, __) => const Center(
                child: Text(
                  '无法加载商品信息',
                  style: TextStyle(color: Colors.white70),
                ),
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          Row(
            children: [
              Expanded(
                child: AnimatedPressButton(
                  onPressed: () => context.router.push(const ShoppingHomeRoute()),
                  child: const Text('全部商品'),
                  backgroundColor: Colors.white,
                  textColor: AppColors.secondaryColor,
                ),
              ),
              const SizedBox(width: 8),
              AnimatedPressButton(
                onPressed: () => context.router.push(const ShoppingCartRoute()),
                child: Row(
                  children: [
                    const Icon(Icons.shopping_cart, size: 20),
                    const SizedBox(width: 4),
                    if (cartItemCount > 0)
                      Container(
                        padding: const EdgeInsets.all(4),
                        decoration: const BoxDecoration(
                          color: Colors.red,
                          shape: BoxShape.circle,
                        ),
                        child: Text(
                          cartItemCount.toString(),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                  ],
                ),
                backgroundColor: AppColors.secondaryDarkColor,
                textColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPromotionBanner(BuildContext context) {
    return Container(
      width: double.infinity,
      height: 70,
      decoration: BoxDecoration(
        color: Colors.white.withAlpha(50),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Stack(
        children: [
          Positioned.fill(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: const Image(
                image: AssetImage('assets/images/shopping_banner.jpg'),
                fit: BoxFit.cover,
              ),
            ),
          ),
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(8),
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.black.withAlpha((0.6 * 255).toInt()),
                    Colors.black.withAlpha((0.3 * 255).toInt()),
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            left: 16,
            top: 16,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const [
                Text(
                  '限时特惠',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  '中医养生好物 低至7折',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProductItem(BuildContext context, dynamic product) {
    return GestureDetector(
      onTap: () => context.router.push(ProductDetailsRoute(productId: product.id)),
      child: Container(
        width: 120,
        margin: const EdgeInsets.only(right: 10),
        decoration: BoxDecoration(
          color: Colors.white.withAlpha(30),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ClipRRect(
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(8),
                topRight: Radius.circular(8),
              ),
              child: Image.network(
                product.imageUrl,
                width: 120,
                height: 80,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) => Container(
                  width: 120,
                  height: 80,
                  color: Colors.grey.withAlpha(70),
                  child: const Icon(
                    Icons.image_not_supported,
                    color: Colors.white70,
                  ),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(6.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    product.name,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '¥${product.discountedPrice.toStringAsFixed(2)}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                    ),
                  ),
                  if (product.hasDiscount)
                    Text(
                      '¥${product.price.toStringAsFixed(2)}',
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 10,
                        decoration: TextDecoration.lineThrough,
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
} 