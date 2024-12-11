import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../core/config/env_config.dart';

class BaseApiService {
  final String appKey;
  final String appSecret;
  final String appCode;
  
  BaseApiService({
    required this.appKey,
    required this.appSecret,
    required this.appCode,
  });

  Map<String, String> get _headers => {
    'Authorization': 'APPCODE $appCode',
    'Content-Type': 'application/json',
  };

  Future<Map<String, dynamic>> post(String url, Map<String, dynamic> body) async {
    try {
      final response = await http.post(
        Uri.parse(url),
        headers: _headers,
        body: json.encode(body),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('API请求失败: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('API请求异常: $e');
    }
  }

  Future<Map<String, dynamic>> get(String url) async {
    try {
      final response = await http.get(
        Uri.parse(url),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('API请求失败: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('API请求异常: $e');
    }
  }
} 