import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'notification_service.dart';

class PaymentService extends GetxService {
  final StorageService _storageService = Get.find();
  final NotificationService _notificationService = Get.find();

  // 创建支付订单
  Future<Map<String, dynamic>> createOrder({
    required String productId,
    required double amount,
    String? description,
  }) async {
    try {
      final order = {
        'id': DateTime.now().toString(),
        'product_id': productId,
        'amount': amount,
        'description': description,
        'status': 'pending',
        'created_at': DateTime.now().toIso8601String(),
      };

      await _saveOrder(order);
      return order;
    } catch (e) {
      rethrow;
    }
  }

  // 处理支付
  Future<void> processPayment(String orderId) async {
    try {
      final orders = await _getOrders();
      final index = orders.indexWhere((o) => o['id'] == orderId);
      
      if (index != -1) {
        orders[index]['status'] = 'processing';
        await _storageService.saveLocal('payment_orders', orders);
        
        print('Calling payment interface for order: $orderId');
        // 示例：调用第三方支付接口
        // 实际实现中需要根据具体支付接口进行调用
        // 例如：await _paymentGateway.processPayment(orderId);
        
        // 支付成功
        await _completePayment(orderId);
      }
    } catch (e) {
      await _failPayment(orderId);
      rethrow;
    }
  }

  Future<void> _completePayment(String orderId) async {
    try {
      final orders = await _getOrders();
      final index = orders.indexWhere((o) => o['id'] == orderId);
      
      if (index != -1) {
        orders[index]['status'] = 'completed';
        orders[index]['completed_at'] = DateTime.now().toIso8601String();
        await _storageService.saveLocal('payment_orders', orders);
        
        await _notificationService.showNotification(
          title: '支付成功',
          body: '订单支付成功',
          payload: '/payment/result/$orderId',
        );
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _failPayment(String orderId) async {
    try {
      final orders = await _getOrders();
      final index = orders.indexWhere((o) => o['id'] == orderId);
      
      if (index != -1) {
        orders[index]['status'] = 'failed';
        await _storageService.saveLocal('payment_orders', orders);
        
        await _notificationService.showNotification(
          title: '支付失败',
          body: '订单支付失败,请重试',
          payload: '/payment/retry/$orderId',
        );
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveOrder(Map<String, dynamic> order) async {
    try {
      final orders = await _getOrders();
      orders.add(order);
      await _storageService.saveLocal('payment_orders', orders);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _getOrders() async {
    try {
      final data = await _storageService.getLocal('payment_orders');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }
} 