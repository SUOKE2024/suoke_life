import '../../core/network/network_service.dart';

abstract class BaseAiService {
  final NetworkService _network;
  final String _apiKey;
  final String _baseUrl;

  BaseAiService(
    this._network, {
    String? apiKey,
    String baseUrl = 'https://ark.cn-beijing.volces.com/api/v3',
  })  : _apiKey = apiKey ?? const String.fromEnvironment('ARK_API_KEY'),
        _baseUrl = baseUrl;

  Future<Map<String, dynamic>> post(
    String endpoint, {
    required Map<String, dynamic> data,
  }) async {
    final response = await _network.post(
      '$_baseUrl$endpoint',
      data: data,
      options: {
        'headers': {
          'Authorization': 'Bearer $_apiKey',
          'Content-Type': 'application/json',
        },
      },
    );
    return response.data;
  }
} 