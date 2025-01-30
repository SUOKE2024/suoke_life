import 'package:get/get.dart';
import '../core/storage/storage_service.dart';

class SupplyChainService extends GetxService {
  final StorageService _storageService = Get.find();

  // 获取供应商列表
  Future<List<Map<String, dynamic>>> getSuppliers() async {
    try {
      final data = await _storageService.getRemote('suppliers');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }

  // 获取产品列表
  Future<List<Map<String, dynamic>>> getProducts({String? supplierId}) async {
    try {
      final data = await _storageService.getRemote('products');
      final products = data != null ? List<Map<String, dynamic>>.from(data) : [];
      
      if (supplierId != null) {
        return products.where((p) => p['supplier_id'] == supplierId).toList();
      }
      return products;
    } catch (e) {
      return [];
    }
  }

  // 库存管理
  Future<void> updateStock(String productId, int quantity) async {
    try {
      final products = await getProducts();
      final index = products.indexWhere((p) => p['id'] == productId);
      
      if (index != -1) {
        products[index]['stock'] = quantity;
        await _storageService.saveRemote('products', products);
      }
    } catch (e) {
      rethrow;
    }
  }

  // 订单处理
  Future<void> processOrder(Map<String, dynamic> order) async {
    try {
      // 检查库存
      await _checkStock(order['items']);
      
      // 更新库存
      await _updateStockForOrder(order['items']);
      
      // 创建物流订单
      await _createLogistics(order);
      
      // 通知供应商
      await _notifySuppliers(order);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _checkStock(List<Map<String, dynamic>> items) async {
    final products = await getProducts();
    
    for (final item in items) {
      final product = products.firstWhere(
        (p) => p['id'] == item['product_id'],
        orElse: () => throw Exception('Product not found'),
      );
      
      if (product['stock'] < item['quantity']) {
        throw Exception('Insufficient stock for ${product['name']}');
      }
    }
  }

  Future<void> _updateStockForOrder(List<Map<String, dynamic>> items) async {
    for (final item in items) {
      await updateStock(
        item['product_id'],
        item['quantity'],
      );
    }
  }

  Future<void> _createLogistics(Map<String, dynamic> order) async {
    print('Creating logistics order...');
    // 示例：将订单信息发送到物流系统
    // 实际实现中需要根据具体物流系统进行订单创建
  }

  Future<void> _notifySuppliers(Map<String, dynamic> order) async {
    print('Notifying suppliers...');
    // 示例：发送通知到供应商系统
    // 实际实现中需要根据具体供应商系统进行通知
  }
} 