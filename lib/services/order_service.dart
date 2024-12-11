import 'dart:async';
import 'package:flutter/foundation.dart';
import '../core/di/service_locator.dart';
import '../core/network/http_client.dart';
import '../services/cart_service.dart';

enum OrderStatus {
  pending,    // 待付款
  paid,       // 已付款
  processing, // 处理中
  shipping,   // 配送中
  delivered,  // 已送达
  completed,  // 已完成
  cancelled,  // 已取消
  refunding,  // 退款中
  refunded,   // 已退款
}

enum LogisticsStatus {
  collected,    // 已揽收
  inTransit,    // 运输中
  delivering,   // 派送中
  delivered,    // 已送达
  exception,    // 异常
  returning,    // 退回中
}

class LogisticsInfo {
  final LogisticsStatus status;
  final String description;
  final DateTime time;
  final String? location;
  final Map<String, dynamic>? extraData;

  LogisticsInfo({
    required this.status,
    required this.description,
    required this.time,
    this.location,
    this.extraData,
  });

  factory LogisticsInfo.fromJson(Map<String, dynamic> json) {
    return LogisticsInfo(
      status: LogisticsStatus.values.firstWhere(
        (e) => e.toString() == 'LogisticsStatus.${json['status']}',
      ),
      description: json['description'],
      time: DateTime.parse(json['time']),
      location: json['location'],
      extraData: json['extra_data'],
    );
  }
}

enum AfterSaleType {
  refundOnly,      // 仅退款
  returnAndRefund, // 退货退款
}

enum AfterSaleStatus {
  pending,    // 待处理
  processing, // 处理中
  approved,   // 已通过
  rejected,   // 已拒绝
  completed,  // 已完成
  cancelled,  // 已取消
}

class AfterSale {
  final String id;
  final String orderId;
  final AfterSaleType type;
  final String reason;
  final String description;
  final List<String> images;
  final List<OrderItem> items;
  final double refundAmount;
  final AfterSaleStatus status;
  final DateTime createdAt;
  final DateTime? updatedAt;

  AfterSale({
    required this.id,
    required this.orderId,
    required this.type,
    required this.reason,
    required this.description,
    required this.images,
    required this.items,
    required this.refundAmount,
    required this.status,
    required this.createdAt,
    this.updatedAt,
  });

  factory AfterSale.fromJson(Map<String, dynamic> json) {
    return AfterSale(
      id: json['id'],
      orderId: json['order_id'],
      type: AfterSaleType.values.firstWhere(
        (e) => e.toString() == 'AfterSaleType.${json['type']}',
      ),
      reason: json['reason'],
      description: json['description'],
      images: List<String>.from(json['images']),
      items: (json['items'] as List)
          .map((item) => OrderItem.fromJson(item))
          .toList(),
      refundAmount: json['refund_amount'].toDouble(),
      status: AfterSaleStatus.values.firstWhere(
        (e) => e.toString() == 'AfterSaleStatus.${json['status']}',
      ),
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : null,
    );
  }
}

class OrderService extends GetxController {
  final HttpClient _httpClient = serviceLocator<HttpClient>();
  final _orderStatusController = StreamController<OrderStatusUpdate>.broadcast();

  Stream<OrderStatusUpdate> get orderStatusStream => _orderStatusController.stream;

  Future<Order> createOrder({
    required List<CartItem> items,
    required String addressId,
    String? remarks,
  }) async {
    try {
      final response = await _httpClient.post(
        '/api/orders',
        body: {
          'items': items.map((item) => item.toJson()).toList(),
          'address_id': addressId,
          'remarks': remarks,
        },
      );

      final order = Order.fromJson(response);
      _orderStatusController.add(
        OrderStatusUpdate(
          orderId: order.id,
          status: order.status,
          timestamp: DateTime.now(),
        ),
      );

      return order;
    } catch (e) {
      debugPrint('Failed to create order: $e');
      rethrow;
    }
  }

  Future<List<Order>> getOrders({
    OrderStatus? status,
    DateTime? startDate,
    DateTime? endDate,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final queryParams = {
        'page': page.toString(),
        'page_size': pageSize.toString(),
        if (status != null) 'status': status.name,
        if (startDate != null) 'start_date': startDate.toIso8601String(),
        if (endDate != null) 'end_date': endDate.toIso8601String(),
      };

      final response = await _httpClient.get(
        '/api/orders',
        queryParameters: queryParams,
      );

      return (response['items'] as List)
          .map((item) => Order.fromJson(item))
          .toList();
    } catch (e) {
      debugPrint('Failed to get orders: $e');
      rethrow;
    }
  }

  Future<Order> getOrderDetails(String orderId) async {
    try {
      final response = await _httpClient.get('/api/orders/$orderId');
      return Order.fromJson(response);
    } catch (e) {
      debugPrint('Failed to get order details: $e');
      rethrow;
    }
  }

  Future<void> cancelOrder(String orderId) async {
    try {
      await _httpClient.post('/api/orders/$orderId/cancel');
      _orderStatusController.add(
        OrderStatusUpdate(
          orderId: orderId,
          status: OrderStatus.cancelled,
          timestamp: DateTime.now(),
        ),
      );
      update();
    } catch (e) {
      debugPrint('Failed to cancel order: $e');
      rethrow;
    }
  }

  Future<void> confirmReceipt(String orderId) async {
    try {
      await _httpClient.post('/api/orders/$orderId/confirm');
      _orderStatusController.add(
        OrderStatusUpdate(
          orderId: orderId,
          status: OrderStatus.completed,
          timestamp: DateTime.now(),
        ),
      );
      update();
    } catch (e) {
      debugPrint('Failed to confirm receipt: $e');
      rethrow;
    }
  }

  Future<RefundRequest> requestRefund({
    required String orderId,
    required String reason,
    required List<String> imageUrls,
    String? description,
  }) async {
    try {
      final response = await _httpClient.post(
        '/api/orders/$orderId/refund',
        body: {
          'reason': reason,
          'image_urls': imageUrls,
          'description': description,
        },
      );

      final refundRequest = RefundRequest.fromJson(response);
      _orderStatusController.add(
        OrderStatusUpdate(
          orderId: orderId,
          status: OrderStatus.refunding,
          timestamp: DateTime.now(),
        ),
      );
      update();

      return refundRequest;
    } catch (e) {
      debugPrint('Failed to request refund: $e');
      rethrow;
    }
  }

  Future<void> submitReview({
    required String orderId,
    required double rating,
    required String content,
    required List<XFile> images,
    required bool isAnonymous,
  }) async {
    try {
      // 上传图片
      List<String> imageUrls = [];
      if (images.isNotEmpty) {
        imageUrls = await _uploadReviewImages(images);
      }

      // 提交评价
      await _httpClient.post(
        '/api/orders/$orderId/reviews',
        data: {
          'rating': rating,
          'content': content,
          'images': imageUrls,
          'isAnonymous': isAnonymous,
        },
      );
    } catch (e) {
      throw Exception('提交评价失败: $e');
    }
  }

  Future<List<String>> _uploadReviewImages(List<XFile> images) async {
    List<String> imageUrls = [];
    for (var image in images) {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          image.path,
          filename: image.name,
        ),
      });

      final response = await _httpClient.post(
        '/api/upload/review-image',
        data: formData,
      );

      imageUrls.add(response.data['url']);
    }
    return imageUrls;
  }

  Future<List<LogisticsInfo>> getLogisticsInfo({
    required String trackingNumber,
    required String trackingCompany,
  }) async {
    try {
      final response = await _httpClient.get(
        '/api/logistics/track',
        queryParameters: {
          'tracking_number': trackingNumber,
          'tracking_company': trackingCompany,
        },
      );

      return (response.data['tracking_info'] as List)
          .map((info) => LogisticsInfo.fromJson(info))
          .toList();
    } catch (e) {
      debugPrint('Failed to get logistics info: $e');
      rethrow;
    }
  }

  Future<void> submitAfterSale({
    required String orderId,
    required AfterSaleType type,
    required String reason,
    required String description,
    required List<XFile> images,
    required List<OrderItem> items,
  }) async {
    try {
      // 上传图片
      List<String> imageUrls = [];
      if (images.isNotEmpty) {
        imageUrls = await _uploadAfterSaleImages(images);
      }

      // 提交售后申请
      await _httpClient.post(
        '/api/orders/$orderId/after-sales',
        data: {
          'type': type.toString().split('.').last,
          'reason': reason,
          'description': description,
          'images': imageUrls,
          'items': items.map((item) => item.id).toList(),
        },
      );
    } catch (e) {
      debugPrint('Failed to submit after-sale: $e');
      rethrow;
    }
  }

  Future<List<String>> _uploadAfterSaleImages(List<XFile> images) async {
    List<String> imageUrls = [];
    for (var image in images) {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          image.path,
          filename: image.name,
        ),
      });

      final response = await _httpClient.post(
        '/api/upload/after-sale-image',
        data: formData,
      );

      imageUrls.add(response.data['url']);
    }
    return imageUrls;
  }

  Future<List<AfterSale>> getAfterSales(String orderId) async {
    try {
      final response = await _httpClient.get('/api/orders/$orderId/after-sales');
      return (response.data['after_sales'] as List)
          .map((json) => AfterSale.fromJson(json))
          .toList();
    } catch (e) {
      debugPrint('Failed to get after-sales: $e');
      rethrow;
    }
  }

  Future<void> cancelAfterSale(String afterSaleId) async {
    try {
      await _httpClient.post('/api/after-sales/$afterSaleId/cancel');
    } catch (e) {
      debugPrint('Failed to cancel after-sale: $e');
      rethrow;
    }
  }

  void dispose() {
    _orderStatusController.close();
  }
}

class Order {
  final String id;
  final String userId;
  final List<OrderItem> items;
  final OrderAddress address;
  final double totalAmount;
  final OrderStatus status;
  final DateTime createTime;
  final DateTime? payTime;
  final DateTime? shipTime;
  final DateTime? deliveryTime;
  final DateTime? completeTime;
  final String? remarks;
  final String? trackingNumber;
  final String? trackingCompany;
  final Map<String, dynamic>? extraData;

  const Order({
    required this.id,
    required this.userId,
    required this.items,
    required this.address,
    required this.totalAmount,
    required this.status,
    required this.createTime,
    this.payTime,
    this.shipTime,
    this.deliveryTime,
    this.completeTime,
    this.remarks,
    this.trackingNumber,
    this.trackingCompany,
    this.extraData,
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'],
      userId: json['user_id'],
      items: (json['items'] as List)
          .map((item) => OrderItem.fromJson(item))
          .toList(),
      address: OrderAddress.fromJson(json['address']),
      totalAmount: json['total_amount'],
      status: OrderStatus.values.byName(json['status']),
      createTime: DateTime.parse(json['create_time']),
      payTime:
          json['pay_time'] != null ? DateTime.parse(json['pay_time']) : null,
      shipTime:
          json['ship_time'] != null ? DateTime.parse(json['ship_time']) : null,
      deliveryTime: json['delivery_time'] != null
          ? DateTime.parse(json['delivery_time'])
          : null,
      completeTime: json['complete_time'] != null
          ? DateTime.parse(json['complete_time'])
          : null,
      remarks: json['remarks'],
      trackingNumber: json['tracking_number'],
      trackingCompany: json['tracking_company'],
      extraData: json['extra_data'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'items': items.map((item) => item.toJson()).toList(),
      'address': address.toJson(),
      'total_amount': totalAmount,
      'status': status.name,
      'create_time': createTime.toIso8601String(),
      'pay_time': payTime?.toIso8601String(),
      'ship_time': shipTime?.toIso8601String(),
      'delivery_time': deliveryTime?.toIso8601String(),
      'complete_time': completeTime?.toIso8601String(),
      'remarks': remarks,
      'tracking_number': trackingNumber,
      'tracking_company': trackingCompany,
      'extra_data': extraData,
    };
  }
}

class OrderItem {
  final String productId;
  final String name;
  final String specification;
  final double price;
  final int quantity;
  final String imageUrl;

  const OrderItem({
    required this.productId,
    required this.name,
    required this.specification,
    required this.price,
    required this.quantity,
    required this.imageUrl,
  });

  factory OrderItem.fromJson(Map<String, dynamic> json) {
    return OrderItem(
      productId: json['product_id'],
      name: json['name'],
      specification: json['specification'],
      price: json['price'],
      quantity: json['quantity'],
      imageUrl: json['image_url'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'product_id': productId,
      'name': name,
      'specification': specification,
      'price': price,
      'quantity': quantity,
      'image_url': imageUrl,
    };
  }
}

class OrderAddress {
  final String id;
  final String name;
  final String phone;
  final String province;
  final String city;
  final String district;
  final String street;
  final String detail;

  const OrderAddress({
    required this.id,
    required this.name,
    required this.phone,
    required this.province,
    required this.city,
    required this.district,
    required this.street,
    required this.detail,
  });

  factory OrderAddress.fromJson(Map<String, dynamic> json) {
    return OrderAddress(
      id: json['id'],
      name: json['name'],
      phone: json['phone'],
      province: json['province'],
      city: json['city'],
      district: json['district'],
      street: json['street'],
      detail: json['detail'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'phone': phone,
      'province': province,
      'city': city,
      'district': district,
      'street': street,
      'detail': detail,
    };
  }

  String get fullAddress => '$province$city$district$street$detail';
}

class OrderStatusUpdate {
  final String orderId;
  final OrderStatus status;
  final DateTime timestamp;

  const OrderStatusUpdate({
    required this.orderId,
    required this.status,
    required this.timestamp,
  });
}

class RefundRequest {
  final String id;
  final String orderId;
  final String reason;
  final List<String> imageUrls;
  final String? description;
  final DateTime createTime;
  final RefundStatus status;

  const RefundRequest({
    required this.id,
    required this.orderId,
    required this.reason,
    required this.imageUrls,
    this.description,
    required this.createTime,
    required this.status,
  });

  factory RefundRequest.fromJson(Map<String, dynamic> json) {
    return RefundRequest(
      id: json['id'],
      orderId: json['order_id'],
      reason: json['reason'],
      imageUrls: List<String>.from(json['image_urls']),
      description: json['description'],
      createTime: DateTime.parse(json['create_time']),
      status: RefundStatus.values.byName(json['status']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'order_id': orderId,
      'reason': reason,
      'image_urls': imageUrls,
      'description': description,
      'create_time': createTime.toIso8601String(),
      'status': status.name,
    };
  }
}

enum RefundStatus {
  pending,   // 待处理
  approved,  // 已同意
  rejected,  // 已拒绝
  completed, // 已完成
} 