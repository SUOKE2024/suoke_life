import 'package:freezed_annotation/freezed_annotation.dart';

part 'shopping.freezed.dart';

@freezed
class Product with _$Product {
  const factory Product({
    required String id,
    required String name,
    required String description,
    required double price,
    required String categoryId,
    required String imageUrl,
    required bool inStock,
    required int stockQuantity,
    @Default(0) double discountPercentage,
    @Default(0) double rating,
    @Default(0) int reviewCount,
    @Default(false) bool isFeatured,
    @Default(false) bool isNew,
    @Default(false) bool isTcmProduct,
    List<String>? tags,
    List<String>? additionalImageUrls,
    Map<String, dynamic>? specifications,
    Map<String, dynamic>? metadata,
  }) = _Product;

  const Product._();

  double get discountedPrice => price * (1 - discountPercentage / 100);
  bool get hasDiscount => discountPercentage > 0;
}

@freezed
class ProductCategory with _$ProductCategory {
  const factory ProductCategory({
    required String id,
    required String name,
    required String description,
    String? imageUrl,
    @Default(false) bool isFeatured,
    @Default(0) int productCount,
    Map<String, dynamic>? metadata,
  }) = _ProductCategory;
}

@freezed
class CartItem with _$CartItem {
  const factory CartItem({
    required String id,
    required String productId,
    required String productName,
    required String productImageUrl,
    required double price,
    required int quantity,
    @Default(0) double discountPercentage,
    String? selectedVariant,
    Map<String, dynamic>? customization,
    DateTime? addedAt,
  }) = _CartItem;

  const CartItem._();

  double get totalPrice => price * quantity * (1 - discountPercentage / 100);
}

@freezed
class ShoppingCart with _$ShoppingCart {
  const factory ShoppingCart({
    required String userId,
    required List<CartItem> items,
    required DateTime updatedAt,
    String? appliedCouponCode,
    double? shippingCost,
    String? note,
  }) = _ShoppingCart;

  const ShoppingCart._();

  double get subtotal => items.fold(0, (sum, item) => sum + item.totalPrice);
  
  double get discount {
    // 此处简化了优惠计算逻辑
    return 0.0;
  }
  
  double get total {
    double total = subtotal - discount;
    if (shippingCost != null) {
      total += shippingCost!;
    }
    return total;
  }
  
  int get itemCount => items.fold(0, (sum, item) => sum + item.quantity);
  
  bool get isEmpty => items.isEmpty;
}

@freezed
class Order with _$Order {
  const factory Order({
    required String id,
    required String userId,
    required List<CartItem> items,
    required double totalAmount,
    required OrderStatus status,
    required DateTime createdAt,
    required String paymentMethod,
    required String shippingAddress,
    required String recipientName,
    required String recipientPhone,
    DateTime? paidAt,
    DateTime? shippedAt,
    DateTime? deliveredAt,
    DateTime? cancelledAt,
    String? trackingNumber,
    String? shippingMethod,
    String? cancellationReason,
    String? note,
    String? couponCode,
    double? discount,
    double? shippingCost,
    Map<String, dynamic>? metadata,
  }) = _Order;

  const Order._();

  bool get isPaid => paidAt != null;
  bool get isShipped => shippedAt != null;
  bool get isDelivered => deliveredAt != null;
  bool get isCancelled => cancelledAt != null;
}

enum OrderStatus {
  pending,
  paid,
  processing,
  shipped,
  delivered,
  cancelled,
  refunded
} 