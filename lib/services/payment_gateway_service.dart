import 'package:dio/dio.dart';
import '../core/config/app_config.dart';

class PaymentGatewayService {
  final Dio _dio;
  final AppConfig _config;

  PaymentGatewayService(this._config) : _dio = Dio() {
    _dio.options.baseUrl = _config.paymentGatewayUrl;
    _dio.options.headers = {
      'Authorization': 'Bearer ${_config.paymentGatewayToken}',
    };
  }

  // 支付宝支付
  Future<Map<String, dynamic>> createAlipayOrder(
    String orderId,
    double amount,
    String subject,
  ) async {
    try {
      final response = await _dio.post('/alipay/create', data: {
        'out_trade_no': orderId,
        'total_amount': amount.toString(),
        'subject': subject,
      });
      return response.data;
    } catch (e) {
      print('创建支付宝订单失败: $e');
      rethrow;
    }
  }

  // 微信支付
  Future<Map<String, dynamic>> createWechatOrder(
    String orderId,
    double amount,
    String description,
  ) async {
    try {
      final response = await _dio.post('/wechat/create', data: {
        'out_trade_no': orderId,
        'total_fee': (amount * 100).toInt(), // 转换为分
        'body': description,
      });
      return response.data;
    } catch (e) {
      print('创建微信支付订单失败: $e');
      rethrow;
    }
  }

  // 银联支付
  Future<Map<String, dynamic>> createUnionpayOrder(
    String orderId,
    double amount,
    String description,
  ) async {
    try {
      final response = await _dio.post('/unionpay/create', data: {
        'orderId': orderId,
        'txnAmt': (amount * 100).toInt(), // 转换为分
        'orderDesc': description,
      });
      return response.data;
    } catch (e) {
      print('创建银联支付订单失败: $e');
      rethrow;
    }
  }

  // 查询支付结果
  Future<Map<String, dynamic>> queryPaymentResult(
    String orderId,
    String paymentMethod,
  ) async {
    try {
      final response = await _dio.get(
        '/$paymentMethod/query',
        queryParameters: {'out_trade_no': orderId},
      );
      return response.data;
    } catch (e) {
      print('查询支付结果失败: $e');
      rethrow;
    }
  }

  // 申请退款
  Future<Map<String, dynamic>> applyRefund(
    String orderId,
    String paymentMethod,
    double amount,
    String reason,
  ) async {
    try {
      final response = await _dio.post('/$paymentMethod/refund', data: {
        'out_trade_no': orderId,
        'refund_amount': amount.toString(),
        'refund_reason': reason,
      });
      return response.data;
    } catch (e) {
      print('申请退款失败: $e');
      rethrow;
    }
  }
} 