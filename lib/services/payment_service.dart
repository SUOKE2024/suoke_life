import 'dart:async';
import 'package:flutter/foundation.dart';
import '../core/di/service_locator.dart';
import '../core/network/http_client.dart';

enum PaymentMethod {
  wechat,
  alipay,
  bankCard,
}

enum PaymentStatus {
  pending,
  processing,
  success,
  failed,
  cancelled,
}

class PaymentService {
  final HttpClient _httpClient = serviceLocator<HttpClient>();
  final _paymentStatusController = StreamController<PaymentStatus>.broadcast();

  Stream<PaymentStatus> get paymentStatusStream => _paymentStatusController.stream;

  Future<String> createPaymentOrder({
    required String orderId,
    required double amount,
    required PaymentMethod method,
    String? description,
  }) async {
    try {
      // TODO: 调用后端API创建支付订单
      final response = await _httpClient.post(
        '/api/payments',
        body: {
          'order_id': orderId,
          'amount': amount,
          'method': method.name,
          'description': description,
        },
      );

      return response['payment_id'];
    } catch (e) {
      debugPrint('Failed to create payment order: $e');
      rethrow;
    }
  }

  Future<void> processPayment({
    required String paymentId,
    required PaymentMethod method,
  }) async {
    try {
      _paymentStatusController.add(PaymentStatus.processing);

      switch (method) {
        case PaymentMethod.wechat:
          await _processWechatPay(paymentId);
          break;
        case PaymentMethod.alipay:
          await _processAlipay(paymentId);
          break;
        case PaymentMethod.bankCard:
          await _processBankCardPay(paymentId);
          break;
      }

      _paymentStatusController.add(PaymentStatus.success);
    } catch (e) {
      _paymentStatusController.add(PaymentStatus.failed);
      debugPrint('Payment failed: $e');
      rethrow;
    }
  }

  Future<void> _processWechatPay(String paymentId) async {
    // TODO: 实现微信支付
    await Future.delayed(const Duration(seconds: 2));
  }

  Future<void> _processAlipay(String paymentId) async {
    // TODO: 实现支付宝支付
    await Future.delayed(const Duration(seconds: 2));
  }

  Future<void> _processBankCardPay(String paymentId) async {
    // TODO: 实现银行卡支付
    await Future.delayed(const Duration(seconds: 2));
  }

  Future<PaymentStatus> checkPaymentStatus(String paymentId) async {
    try {
      final response = await _httpClient.get('/api/payments/$paymentId/status');
      return PaymentStatus.values.byName(response['status']);
    } catch (e) {
      debugPrint('Failed to check payment status: $e');
      rethrow;
    }
  }

  Future<void> cancelPayment(String paymentId) async {
    try {
      await _httpClient.post('/api/payments/$paymentId/cancel');
      _paymentStatusController.add(PaymentStatus.cancelled);
    } catch (e) {
      debugPrint('Failed to cancel payment: $e');
      rethrow;
    }
  }

  void dispose() {
    _paymentStatusController.close();
  }
}

class PaymentResult {
  final String paymentId;
  final PaymentStatus status;
  final String? transactionId;
  final DateTime timestamp;
  final Map<String, dynamic>? extraData;

  const PaymentResult({
    required this.paymentId,
    required this.status,
    this.transactionId,
    required this.timestamp,
    this.extraData,
  });

  factory PaymentResult.fromJson(Map<String, dynamic> json) {
    return PaymentResult(
      paymentId: json['payment_id'],
      status: PaymentStatus.values.byName(json['status']),
      transactionId: json['transaction_id'],
      timestamp: DateTime.parse(json['timestamp']),
      extraData: json['extra_data'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'payment_id': paymentId,
      'status': status.name,
      'transaction_id': transactionId,
      'timestamp': timestamp.toIso8601String(),
      'extra_data': extraData,
    };
  }
} 