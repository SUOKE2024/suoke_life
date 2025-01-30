import 'dart:convert';
import 'package:http/http.dart' as http;

class NetworkService {
  final String baseUrl;
  final Map<String, String> defaultHeaders;

  NetworkService({
    this.baseUrl = '',
    this.defaultHeaders = const {
      'Content-Type': 'application/json',
    },
  });

  Future<void> init() async {
    // 初始化网络服务，比如设置证书等
  }

  Future<Map<String, dynamic>> get(
    String path, {
    Map<String, String>? headers,
    Map<String, dynamic>? queryParameters,
  }) async {
    final uri = Uri.parse(baseUrl + path).replace(
      queryParameters: queryParameters,
    );

    final response = await http.get(
      uri,
      headers: {...defaultHeaders, ...?headers},
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load data: ${response.statusCode}');
    }
  }

  Future<Map<String, dynamic>> post(
    String path, {
    Map<String, String>? headers,
    Map<String, dynamic>? data,
  }) async {
    final uri = Uri.parse(baseUrl + path);

    final response = await http.post(
      uri,
      headers: {...defaultHeaders, ...?headers},
      body: json.encode(data),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to post data: ${response.statusCode}');
    }
  }

  Future<Map<String, dynamic>> put(
    String path, {
    Map<String, String>? headers,
    Map<String, dynamic>? data,
  }) async {
    final uri = Uri.parse(baseUrl + path);

    final response = await http.put(
      uri,
      headers: {...defaultHeaders, ...?headers},
      body: json.encode(data),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to put data: ${response.statusCode}');
    }
  }

  Future<void> delete(
    String path, {
    Map<String, String>? headers,
  }) async {
    final uri = Uri.parse(baseUrl + path);

    final response = await http.delete(
      uri,
      headers: {...defaultHeaders, ...?headers},
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to delete data: ${response.statusCode}');
    }
  }
} 