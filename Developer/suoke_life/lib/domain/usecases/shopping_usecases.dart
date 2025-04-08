import 'package:dartz/dartz.dart';
import '../entities/shopping.dart';
import '../repositories/shopping_repository.dart';
import '../../core/utils/failure.dart';

class GetProductCategoriesUseCase {
  final ShoppingRepository repository;

  GetProductCategoriesUseCase({required this.repository});

  Future<Either<Failure, List<ProductCategory>>> call() async {
    return await repository.getProductCategories();
  }
}

class GetProductsByCategoryUseCase {
  final ShoppingRepository repository;

  GetProductsByCategoryUseCase({required this.repository});

  Future<Either<Failure, List<Product>>> call(String categoryId) async {
    return await repository.getProductsByCategory(categoryId);
  }
}

class GetFeaturedProductsUseCase {
  final ShoppingRepository repository;

  GetFeaturedProductsUseCase({required this.repository});

  Future<Either<Failure, List<Product>>> call() async {
    return await repository.getFeaturedProducts();
  }
}

class GetProductDetailsUseCase {
  final ShoppingRepository repository;

  GetProductDetailsUseCase({required this.repository});

  Future<Either<Failure, Product>> call(String productId) async {
    return await repository.getProductDetails(productId);
  }
}

class SearchProductsUseCase {
  final ShoppingRepository repository;

  SearchProductsUseCase({required this.repository});

  Future<Either<Failure, List<Product>>> call(String query, {String? categoryId}) async {
    return await repository.searchProducts(query, categoryId: categoryId);
  }
}

class GetShoppingCartUseCase {
  final ShoppingRepository repository;

  GetShoppingCartUseCase({required this.repository});

  Future<Either<Failure, ShoppingCart>> call() async {
    return await repository.getShoppingCart();
  }
}

class AddToCartUseCase {
  final ShoppingRepository repository;

  AddToCartUseCase({required this.repository});

  Future<Either<Failure, ShoppingCart>> call({
    required String productId,
    required String productName,
    required String productImageUrl,
    required double price,
    required int quantity,
    double discountPercentage = 0,
    String? selectedVariant,
    Map<String, dynamic>? customization,
  }) async {
    return await repository.addToCart(
      productId: productId,
      productName: productName,
      productImageUrl: productImageUrl,
      price: price,
      quantity: quantity,
      discountPercentage: discountPercentage,
      selectedVariant: selectedVariant,
      customization: customization,
    );
  }
}

class UpdateCartItemUseCase {
  final ShoppingRepository repository;

  UpdateCartItemUseCase({required this.repository});

  Future<Either<Failure, ShoppingCart>> call({
    required String cartItemId,
    required int quantity,
  }) async {
    return await repository.updateCartItem(
      cartItemId: cartItemId,
      quantity: quantity,
    );
  }
}

class RemoveFromCartUseCase {
  final ShoppingRepository repository;

  RemoveFromCartUseCase({required this.repository});

  Future<Either<Failure, ShoppingCart>> call(String cartItemId) async {
    return await repository.removeFromCart(cartItemId);
  }
}

class ApplyCouponUseCase {
  final ShoppingRepository repository;

  ApplyCouponUseCase({required this.repository});

  Future<Either<Failure, ShoppingCart>> call(String couponCode) async {
    return await repository.applyCoupon(couponCode);
  }
}

class PlaceOrderUseCase {
  final ShoppingRepository repository;

  PlaceOrderUseCase({required this.repository});

  Future<Either<Failure, Order>> call({
    required String paymentMethod,
    required String shippingAddress,
    required String recipientName,
    required String recipientPhone,
    String? shippingMethod,
    String? note,
    String? couponCode,
  }) async {
    return await repository.placeOrder(
      paymentMethod: paymentMethod,
      shippingAddress: shippingAddress,
      recipientName: recipientName,
      recipientPhone: recipientPhone,
      shippingMethod: shippingMethod,
      note: note,
      couponCode: couponCode,
    );
  }
}

class GetUserOrdersUseCase {
  final ShoppingRepository repository;

  GetUserOrdersUseCase({required this.repository});

  Future<Either<Failure, List<Order>>> call() async {
    return await repository.getUserOrders();
  }
} 