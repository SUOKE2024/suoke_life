import 'dart:async';
import 'package:flutter/foundation.dart';
import '../core/di/service_locator.dart';
import '../core/network/http_client.dart';
import 'package:dio/dio.dart';
import '../data/remote/mysql/knowledge_database.dart';
import 'dart:convert';

enum PaymentMethod {
  alipay,    // 支付宝
  wechat,    // 微信支付
  unionpay,  // 银联
  balance,   // 余额支付
}

enum PaymentStatus {
  pending,    // 待支付
  processing, // 处理中
  success,    // 支付成功
  failed,     // 支付失败
  refunding,  // 退款中
  refunded,   // 已退款
}

class PaymentService {
  final KnowledgeDatabase _knowledgeDb;
  final Dio _dio;

  PaymentService(this._knowledgeDb) : _dio = Dio();

  // 处理支付
  Future<Map<String, dynamic>> processPayment(
    String orderId,
    double amount,
    String paymentMethod,
  ) async {
    try {
      // 记录支付请求
      final paymentId = await _createPaymentRecord(
        orderId,
        amount,
        paymentMethod,
      );

      // 调用支付网关
      final response = await _callPaymentGateway(
        paymentId,
        amount,
        paymentMethod,
      );

      // 更新支付记录
      await _updatePaymentRecord(
        paymentId,
        response['success'] ? PaymentStatus.success : PaymentStatus.failed,
        response,
      );

      return response;
    } catch (e) {
      print('支付处理失败: $e');
      return {'success': false, 'error': e.toString()};
    }
  }

  // 处理退款
  Future<Map<String, dynamic>> processRefund(
    String orderId,
    double amount,
    String reason,
  ) async {
    try {
      // 获取原支付记录
      final paymentRecord = await _getPaymentRecord(orderId);
      if (paymentRecord == null) {
        return {'success': false, 'error': '未找到支付记录'};
      }

      // 创建退款记录
      final refundId = await _createRefundRecord(
        orderId,
        amount,
        reason,
      );

      // 调用退款接口
      final response = await _callRefundGateway(
        refundId,
        amount,
        paymentRecord['payment_method'],
      );

      // 更新退款记录
      await _updateRefundRecord(
        refundId,
        response['success'] ? PaymentStatus.refunded : PaymentStatus.failed,
        response,
      );

      return response;
    } catch (e) {
      print('退款处理失败: $e');
      return {'success': false, 'error': e.toString()};
    }
  }

  // 内部方法
  Future<String> _createPaymentRecord(
    String orderId,
    double amount,
    String paymentMethod,
  ) async {
    final paymentId = DateTime.now().millisecondsSinceEpoch.toString();
    await _knowledgeDb._conn.query('''
      INSERT INTO payments (
        id, order_id, amount, payment_method, status, created_at
      ) VALUES (?, ?, ?, ?, ?, NOW())
    ''', [paymentId, orderId, amount, paymentMethod, PaymentStatus.pending.name]);
    return paymentId;
  }

  Future<Map<String, dynamic>?> _getPaymentRecord(String orderId) async {
    final results = await _knowledgeDb._conn.query(
      'SELECT * FROM payments WHERE order_id = ? ORDER BY created_at DESC LIMIT 1',
      [orderId],
    );
    if (results.isEmpty) return null;
    return results.first.fields;
  }

  Future<void> _updatePaymentRecord(
    String paymentId,
    PaymentStatus status,
    Map<String, dynamic> response,
  ) async {
    await _knowledgeDb._conn.query('''
      UPDATE payments 
      SET status = ?, response_data = ?, updated_at = NOW()
      WHERE id = ?
    ''', [status.name, jsonEncode(response), paymentId]);
  }

  // ... 其他内部方法实现
} 