import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/shopping.dart';
import '../../data/repositories/shopping_repository_impl.dart';
import '../../data/datasources/remote/shopping_api_service.dart';
import '../../domain/usecases/shopping_usecases.dart';
import '../../presentation/suoke/providers/shopping_provider.dart';
import '../providers/core_providers.dart';

// 购物API服务Provider
final shoppingApiServiceProvider = Provider<ShoppingApiService>((ref) {
  final dio = ref.watch(dioProvider);
  return ShoppingApiServiceImpl(dio);
});

// 购物数据源Provider
final shoppingRemoteDataSourceProvider = Provider<ShoppingRemoteDataSource>((ref) {
  final dio = ref.watch(dioProvider);
  final apiService = ref.watch(shoppingApiServiceProvider);
  return ShoppingRemoteDataSourceImpl(dio: dio, apiService: apiService);
});

final shoppingLocalDataSourceProvider = Provider<ShoppingLocalDataSource>((ref) {
  final database = ref.watch(databaseProvider);
  return ShoppingLocalDataSourceImpl(database: database);
});

// 购物仓库Provider
final shoppingRepositoryProvider = Provider<ShoppingRepository>((ref) {
  final remoteDataSource = ref.watch(shoppingRemoteDataSourceProvider);
  final localDataSource = ref.watch(shoppingLocalDataSourceProvider);
  return ShoppingRepositoryImpl(
    remoteDataSource: remoteDataSource,
    localDataSource: localDataSource,
  );
});

// 购物用例Provider
final getProductCategoriesUseCaseProvider = Provider<GetProductCategoriesUseCase>((ref) {
  return GetProductCategoriesUseCase(repository: ref.watch(shoppingRepositoryProvider));
});

final getProductsByCategoryUseCaseProvider = Provider<GetProductsByCategoryUseCase>((ref) {
  return GetProductsByCategoryUseCase(repository: ref.watch(shoppingRepositoryProvider));
});

final getFeaturedProductsUseCaseProvider = Provider<GetFeaturedProductsUseCase>((ref) {
  return GetFeaturedProductsUseCase(repository: ref.watch(shoppingRepositoryProvider));
});

final getProductDetailsUseCaseProvider = Provider<GetProductDetailsUseCase>((ref) {
  return GetProductDetailsUseCase(repository: ref.watch(shoppingRepositoryProvider));
});

final getShoppingCartUseCaseProvider = Provider<GetShoppingCartUseCase>((ref) {
  return GetShoppingCartUseCase(repository: ref.watch(shoppingRepositoryProvider));
});

final addToCartUseCaseProvider = Provider<AddToCartUseCase>((ref) {
  return AddToCartUseCase(repository: ref.watch(shoppingRepositoryProvider));
});

final updateCartItemUseCaseProvider = Provider<UpdateCartItemUseCase>((ref) {
  return UpdateCartItemUseCase(repository: ref.watch(shoppingRepositoryProvider));
});

final removeFromCartUseCaseProvider = Provider<RemoveFromCartUseCase>((ref) {
  return RemoveFromCartUseCase(repository: ref.watch(shoppingRepositoryProvider));
});

final placeOrderUseCaseProvider = Provider<PlaceOrderUseCase>((ref) {
  return PlaceOrderUseCase(repository: ref.watch(shoppingRepositoryProvider));
});

final getUserOrdersUseCaseProvider = Provider<GetUserOrdersUseCase>((ref) {
  return GetUserOrdersUseCase(repository: ref.watch(shoppingRepositoryProvider));
});

// 购物控制器Provider
final shoppingControllerProvider = StateNotifierProvider<ShoppingController, ShoppingState>((ref) {
  return ShoppingController(
    getProductCategoriesUseCase: ref.watch(getProductCategoriesUseCaseProvider),
    getProductsByCategoryUseCase: ref.watch(getProductsByCategoryUseCaseProvider),
    getFeaturedProductsUseCase: ref.watch(getFeaturedProductsUseCaseProvider),
    getProductDetailsUseCase: ref.watch(getProductDetailsUseCaseProvider),
    getShoppingCartUseCase: ref.watch(getShoppingCartUseCaseProvider),
    addToCartUseCase: ref.watch(addToCartUseCaseProvider),
    updateCartItemUseCase: ref.watch(updateCartItemUseCaseProvider),
    removeFromCartUseCase: ref.watch(removeFromCartUseCaseProvider),
  );
});

// 购物数据提供Provider
final productCategoriesProvider = Provider<AsyncValue<List<ProductCategory>>>((ref) {
  final controller = ref.watch(shoppingControllerProvider);
  return controller.categories;
});

final featuredProductsProvider = Provider<AsyncValue<List<Product>>>((ref) {
  final controller = ref.watch(shoppingControllerProvider);
  return controller.featuredProducts;
});

final currentCategoryProductsProvider = Provider<AsyncValue<List<Product>>>((ref) {
  final controller = ref.watch(shoppingControllerProvider);
  return controller.currentCategoryProducts;
});

final selectedProductProvider = Provider<AsyncValue<Product?>>((ref) {
  final controller = ref.watch(shoppingControllerProvider);
  return controller.selectedProduct;
});

final shoppingCartProvider = Provider<AsyncValue<ShoppingCart?>>((ref) {
  final controller = ref.watch(shoppingControllerProvider);
  return controller.cart;
});

final cartItemCountProvider = Provider<int>((ref) {
  final cart = ref.watch(shoppingCartProvider);
  return cart.when(
    data: (cart) => cart?.itemCount ?? 0,
    loading: () => 0,
    error: (_, __) => 0,
  );
});

// 订单控制器Provider
final orderControllerProvider = StateNotifierProvider<OrderController, OrderState>((ref) {
  return OrderController(
    placeOrderUseCase: ref.watch(placeOrderUseCaseProvider),
    getUserOrdersUseCase: ref.watch(getUserOrdersUseCaseProvider),
  );
});

final userOrdersProvider = Provider<AsyncValue<List<Order>>>((ref) {
  final controller = ref.watch(orderControllerProvider);
  return controller.orders;
});

final selectedOrderProvider = Provider<AsyncValue<Order?>>((ref) {
  final controller = ref.watch(orderControllerProvider);
  return controller.selectedOrder;
}); 