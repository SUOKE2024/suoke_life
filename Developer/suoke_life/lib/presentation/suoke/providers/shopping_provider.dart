import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../domain/entities/shopping.dart';
import '../../../domain/usecases/shopping_usecases.dart';

// 购物控制器状态
class ShoppingState {
  final AsyncValue<List<ProductCategory>> categories;
  final AsyncValue<List<Product>> featuredProducts;
  final AsyncValue<List<Product>> currentCategoryProducts;
  final AsyncValue<Product?> selectedProduct;
  final AsyncValue<ShoppingCart?> cart;
  final String currentCategoryId;
  final String searchQuery;

  ShoppingState({
    this.categories = const AsyncValue.loading(),
    this.featuredProducts = const AsyncValue.loading(),
    this.currentCategoryProducts = const AsyncValue.loading(),
    this.selectedProduct = const AsyncValue.loading(),
    this.cart = const AsyncValue.loading(),
    this.currentCategoryId = '',
    this.searchQuery = '',
  });

  ShoppingState copyWith({
    AsyncValue<List<ProductCategory>>? categories,
    AsyncValue<List<Product>>? featuredProducts,
    AsyncValue<List<Product>>? currentCategoryProducts,
    AsyncValue<Product?>? selectedProduct,
    AsyncValue<ShoppingCart?>? cart,
    String? currentCategoryId,
    String? searchQuery,
  }) {
    return ShoppingState(
      categories: categories ?? this.categories,
      featuredProducts: featuredProducts ?? this.featuredProducts,
      currentCategoryProducts: currentCategoryProducts ?? this.currentCategoryProducts,
      selectedProduct: selectedProduct ?? this.selectedProduct,
      cart: cart ?? this.cart,
      currentCategoryId: currentCategoryId ?? this.currentCategoryId,
      searchQuery: searchQuery ?? this.searchQuery,
    );
  }
}

// 购物控制器
class ShoppingController extends StateNotifier<ShoppingState> {
  final GetProductCategoriesUseCase getProductCategoriesUseCase;
  final GetProductsByCategoryUseCase getProductsByCategoryUseCase;
  final GetFeaturedProductsUseCase getFeaturedProductsUseCase;
  final GetProductDetailsUseCase getProductDetailsUseCase;
  final GetShoppingCartUseCase getShoppingCartUseCase;
  final AddToCartUseCase addToCartUseCase;
  final UpdateCartItemUseCase updateCartItemUseCase;
  final RemoveFromCartUseCase removeFromCartUseCase;

  ShoppingController({
    required this.getProductCategoriesUseCase,
    required this.getProductsByCategoryUseCase,
    required this.getFeaturedProductsUseCase,
    required this.getProductDetailsUseCase,
    required this.getShoppingCartUseCase,
    required this.addToCartUseCase,
    required this.updateCartItemUseCase,
    required this.removeFromCartUseCase,
  }) : super(ShoppingState()) {
    // 初始化时自动加载数据
    loadInitialData();
  }

  Future<void> loadInitialData() async {
    await Future.wait([
      loadCategories(),
      loadFeaturedProducts(),
      loadShoppingCart(),
    ]);
  }

  Future<void> loadCategories() async {
    final result = await getProductCategoriesUseCase();
    result.fold(
      (failure) => state = state.copyWith(
        categories: AsyncValue.error(failure, StackTrace.current),
      ),
      (categories) => state = state.copyWith(
        categories: AsyncValue.data(categories),
      ),
    );
  }

  Future<void> loadFeaturedProducts() async {
    final result = await getFeaturedProductsUseCase();
    result.fold(
      (failure) => state = state.copyWith(
        featuredProducts: AsyncValue.error(failure, StackTrace.current),
      ),
      (products) => state = state.copyWith(
        featuredProducts: AsyncValue.data(products),
      ),
    );
  }

  Future<void> loadProductsByCategory(String categoryId) async {
    state = state.copyWith(
      currentCategoryId: categoryId,
      currentCategoryProducts: const AsyncValue.loading(),
    );

    final result = await getProductsByCategoryUseCase(categoryId);
    result.fold(
      (failure) => state = state.copyWith(
        currentCategoryProducts: AsyncValue.error(failure, StackTrace.current),
      ),
      (products) => state = state.copyWith(
        currentCategoryProducts: AsyncValue.data(products),
      ),
    );
  }

  Future<void> loadProductDetails(String productId) async {
    state = state.copyWith(
      selectedProduct: const AsyncValue.loading(),
    );

    final result = await getProductDetailsUseCase(productId);
    result.fold(
      (failure) => state = state.copyWith(
        selectedProduct: AsyncValue.error(failure, StackTrace.current),
      ),
      (product) => state = state.copyWith(
        selectedProduct: AsyncValue.data(product),
      ),
    );
  }

  Future<void> loadShoppingCart() async {
    final result = await getShoppingCartUseCase();
    result.fold(
      (failure) => state = state.copyWith(
        cart: AsyncValue.error(failure, StackTrace.current),
      ),
      (cart) => state = state.copyWith(
        cart: AsyncValue.data(cart),
      ),
    );
  }

  Future<void> addToCart({
    required String productId,
    required String productName,
    required String productImageUrl,
    required double price,
    required int quantity,
    double discountPercentage = 0,
    String? selectedVariant,
    Map<String, dynamic>? customization,
  }) async {
    final result = await addToCartUseCase(
      productId: productId,
      productName: productName,
      productImageUrl: productImageUrl,
      price: price,
      quantity: quantity,
      discountPercentage: discountPercentage,
      selectedVariant: selectedVariant,
      customization: customization,
    );

    result.fold(
      (failure) => state = state.copyWith(
        cart: AsyncValue.error(failure, StackTrace.current),
      ),
      (updatedCart) => state = state.copyWith(
        cart: AsyncValue.data(updatedCart),
      ),
    );
  }

  Future<void> updateCartItem({
    required String cartItemId,
    required int quantity,
  }) async {
    final result = await updateCartItemUseCase(
      cartItemId: cartItemId,
      quantity: quantity,
    );

    result.fold(
      (failure) => state = state.copyWith(
        cart: AsyncValue.error(failure, StackTrace.current),
      ),
      (updatedCart) => state = state.copyWith(
        cart: AsyncValue.data(updatedCart),
      ),
    );
  }

  Future<void> removeFromCart(String cartItemId) async {
    final result = await removeFromCartUseCase(cartItemId);

    result.fold(
      (failure) => state = state.copyWith(
        cart: AsyncValue.error(failure, StackTrace.current),
      ),
      (updatedCart) => state = state.copyWith(
        cart: AsyncValue.data(updatedCart),
      ),
    );
  }

  void setSearchQuery(String query) {
    state = state.copyWith(searchQuery: query);
  }
}

// 订单控制器状态
class OrderState {
  final AsyncValue<List<Order>> orders;
  final AsyncValue<Order?> selectedOrder;
  final AsyncValue<Order?> lastPlacedOrder;

  OrderState({
    this.orders = const AsyncValue.loading(),
    this.selectedOrder = const AsyncValue.loading(),
    this.lastPlacedOrder = const AsyncValue.loading(),
  });

  OrderState copyWith({
    AsyncValue<List<Order>>? orders,
    AsyncValue<Order?>? selectedOrder,
    AsyncValue<Order?>? lastPlacedOrder,
  }) {
    return OrderState(
      orders: orders ?? this.orders,
      selectedOrder: selectedOrder ?? this.selectedOrder,
      lastPlacedOrder: lastPlacedOrder ?? this.lastPlacedOrder,
    );
  }
}

// 订单控制器
class OrderController extends StateNotifier<OrderState> {
  final PlaceOrderUseCase placeOrderUseCase;
  final GetUserOrdersUseCase getUserOrdersUseCase;

  OrderController({
    required this.placeOrderUseCase,
    required this.getUserOrdersUseCase,
  }) : super(OrderState()) {
    loadUserOrders();
  }

  Future<void> loadUserOrders() async {
    final result = await getUserOrdersUseCase();
    result.fold(
      (failure) => state = state.copyWith(
        orders: AsyncValue.error(failure, StackTrace.current),
      ),
      (orders) => state = state.copyWith(
        orders: AsyncValue.data(orders),
      ),
    );
  }

  Future<void> loadOrderDetails(String orderId) async {
    state = state.copyWith(
      selectedOrder: const AsyncValue.loading(),
    );

    final result = await getUserOrdersUseCase();
    result.fold(
      (failure) => state = state.copyWith(
        selectedOrder: AsyncValue.error(failure, StackTrace.current),
      ),
      (orders) {
        final selectedOrder = orders.firstWhere(
          (order) => order.id == orderId,
          orElse: () => throw Exception('Order not found'),
        );
        state = state.copyWith(
          selectedOrder: AsyncValue.data(selectedOrder),
        );
      },
    );
  }

  Future<void> placeOrder({
    required String paymentMethod,
    required String shippingAddress,
    required String recipientName,
    required String recipientPhone,
    String? shippingMethod,
    String? note,
    String? couponCode,
  }) async {
    final result = await placeOrderUseCase(
      paymentMethod: paymentMethod,
      shippingAddress: shippingAddress,
      recipientName: recipientName,
      recipientPhone: recipientPhone,
      shippingMethod: shippingMethod,
      note: note,
      couponCode: couponCode,
    );

    result.fold(
      (failure) => state = state.copyWith(
        lastPlacedOrder: AsyncValue.error(failure, StackTrace.current),
      ),
      (order) {
        state = state.copyWith(
          lastPlacedOrder: AsyncValue.data(order),
        );
        loadUserOrders();
      },
    );
  }
} 