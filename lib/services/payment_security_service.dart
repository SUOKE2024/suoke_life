import 'package:crypto/crypto.dart';
import 'dart:convert';
import '../core/config/app_config.dart';

class PaymentSecurityService {
  final AppConfig _config;
  final String _merchantId;
  final String _secretKey;

  PaymentSecurityService(this._config)
      : _merchantId = _config.paymentMerchantId,
        _secretKey = _config.paymentSecretKey;

  // 生成签名
  String generateSignature(Map<String, dynamic> params) {
    // 1. 参数排序
    final sortedParams = Map.fromEntries(
      params.entries.toList()..sort((a, b) => a.key.compareTo(b.key))
    );

    // 2. 拼接参数
    final stringToSign = sortedParams.entries
        .where((e) => e.value != null && e.value.toString().isNotEmpty)
        .map((e) => '${e.key}=${e.value}')
        .join('&');

    // 3. 加入商户ID和时间戳
    final timestamp = DateTime.now().millisecondsSinceEpoch.toString();
    final signString = '$stringToSign&merchant_id=$_merchantId&timestamp=$timestamp';

    // 4. 使用密钥签名
    final key = utf8.encode(_secretKey);
    final bytes = utf8.encode(signString);
    final hmac = Hmac(sha256, key);
    final digest = hmac.convert(bytes);

    return digest.toString();
  }

  // 验证签名
  bool verifySignature(Map<String, dynamic> params, String signature) {
    final calculatedSignature = generateSignature(params);
    return calculatedSignature == signature;
  }

  // 敏感数据加密
  String encryptSensitiveData(String data) {
    // 实现敏感数据加密逻辑
    // 可以使用AES等对称加密算法
    return data; // TODO: 实现加密
  }

  // 防重放攻击验证
  bool validateNonce(String nonce, String timestamp) {
    // TODO: 实现nonce验证逻辑
    // 1. 检查时间戳是否在有效期内
    // 2. 检查nonce是否已使用
    return true;
  }
} 