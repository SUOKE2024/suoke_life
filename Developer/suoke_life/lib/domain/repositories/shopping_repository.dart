import 'package:dartz/dartz.dart';
import '../entities/shopping.dart';
import '../../core/utils/failure.dart';

abstract class ShoppingRepository {
  /// 获取所有商品分类
  Future<Either<Failure, List<ProductCategory>>> getProductCategories();
  
  /// 获取指定分类下的商品
  Future<Either<Failure, List<Product>>> getProductsByCategory(String categoryId);
  
  /// 获取推荐/精选商品
  Future<Either<Failure, List<Product>>> getFeaturedProducts();
  
  /// 获取商品详情
  Future<Either<Failure, Product>> getProductDetails(String productId);
  
  /// 搜索商品
  Future<Either<Failure, List<Product>>> searchProducts(String query, {String? categoryId});
  
  /// 获取购物车
  Future<Either<Failure, ShoppingCart>> getShoppingCart();
  
  /// 添加商品到购物车
  Future<Either<Failure, ShoppingCart>> addToCart({
    required String productId,
    required String productName,
    required String productImageUrl,
    required double price,
    required int quantity,
    double discountPercentage = 0,
    String? selectedVariant,
    Map<String, dynamic>? customization,
  });
  
  /// 更新购物车商品数量
  Future<Either<Failure, ShoppingCart>> updateCartItem({
    required String cartItemId,
    required int quantity,
  });
  
  /// 从购物车移除商品
  Future<Either<Failure, ShoppingCart>> removeFromCart(String cartItemId);
  
  /// 应用优惠券
  Future<Either<Failure, ShoppingCart>> applyCoupon(String couponCode);
  
  /// 创建订单
  Future<Either<Failure, Order>> placeOrder({
    required String paymentMethod,
    required String shippingAddress,
    required String recipientName,
    required String recipientPhone,
    String? shippingMethod,
    String? note,
    String? couponCode,
  });
  
  /// 获取用户订单列表
  Future<Either<Failure, List<Order>>> getUserOrders();
} 