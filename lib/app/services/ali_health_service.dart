import 'package:get/get.dart';
import 'package:crypto/crypto.dart';
import 'dart:convert';
import '../core/network/api_client.dart';
import '../core/config/ali_health_config.dart';
import '../data/models/health_data.dart';
import '../data/models/vital_signs.dart';

class AliHealthService extends GetxService {
  final ApiClient _apiClient;
  
  AliHealthService({required ApiClient apiClient}) : _apiClient = apiClient;

  // 生成签名
  String _generateSignature(Map<String, dynamic> params, String method) {
    final sortedParams = Map.fromEntries(
      params.entries.toList()..sort((a, b) => a.key.compareTo(b.key))
    );

    final signStr = sortedParams.entries
        .map((e) => '${e.key}=${e.value}')
        .join('&');

    final key = utf8.encode(AliHealthConfig.appSecret);
    final bytes = utf8.encode(method + '&' + Uri.encodeFull(signStr));
    
    final hmac = Hmac(sha256, key);
    final digest = hmac.convert(bytes);
    
    return base64.encode(digest.bytes);
  }

  // 健康检查
  Future<HealthData> healthCheck(Map<String, dynamic> data) async {
    try {
      final service = AliHealthConfig.services['health_check']!;
      final params = {
        'app_key': AliHealthConfig.appKey,
        'method': service['method'],
        'version': service['version'],
        'format': AliHealthConfig.format,
        'timestamp': DateTime.now().toUtc().toIso8601String(),
        'sign_method': AliHealthConfig.signMethod,
        ...data,
      };

      params['sign'] = _generateSignature(params, service['method']);

      final response = await _apiClient.post(
        service['path'],
        data: params,
      );

      return HealthData.fromJson(response);
    } catch (e) {
      rethrow;
    }
  }

  // 生命体征监测
  Future<VitalSigns> getVitalSigns(String userId) async {
    try {
      final service = AliHealthConfig.services['vital_signs']!;
      final params = {
        'app_key': AliHealthConfig.appKey,
        'method': service['method'],
        'version': service['version'],
        'format': AliHealthConfig.format,
        'timestamp': DateTime.now().toUtc().toIso8601String(),
        'sign_method': AliHealthConfig.signMethod,
        'user_id': userId,
      };

      params['sign'] = _generateSignature(params, service['method']);

      final response = await _apiClient.get(
        service['path'],
        queryParameters: params,
      );

      return VitalSigns.fromJson(response);
    } catch (e) {
      rethrow;
    }
  }

  // 获取医疗建议
  Future<Map<String, dynamic>> getMedicalAdvice(Map<String, dynamic> data) async {
    try {
      final service = AliHealthConfig.services['medical_advice']!;
      final params = {
        'app_key': AliHealthConfig.appKey,
        'method': service['method'],
        'version': service['version'],
        'format': AliHealthConfig.format,
        'timestamp': DateTime.now().toUtc().toIso8601String(),
        'sign_method': AliHealthConfig.signMethod,
        ...data,
      };

      params['sign'] = _generateSignature(params, service['method']);

      final response = await _apiClient.post(
        service['path'],
        data: params,
      );

      return response;
    } catch (e) {
      rethrow;
    }
  }
} 