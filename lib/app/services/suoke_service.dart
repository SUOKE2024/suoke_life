import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../core/config/suoke_config.dart';
import '../data/models/health_survey.dart';
import '../data/models/tcm_constitution.dart';

class SuokeService extends GetxService {
  final _healthClient = http.Client();
  final _agriClient = http.Client();
  final Map<String, http.Client> _thirdPartyClients = {};

  Future<SuokeService> init() async {
    // 初始化第三方 API 客户端
    for (final api in SuokeConfig.thirdPartyApis.keys) {
      _thirdPartyClients[api] = http.Client();
    }
    return this;
  }

  // 健康问卷服务
  Future<HealthSurvey> submitHealthSurvey(Map<String, dynamic> data) async {
    try {
      final response = await _healthClient.post(
        Uri.parse('${SuokeConfig.healthApiUrl}/surveys'),
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': SuokeConfig.healthApiKey,
        },
        body: jsonEncode(data),
      );

      if (response.statusCode == 200) {
        return HealthSurvey.fromMap(jsonDecode(response.body));
      } else {
        throw Exception('Failed to submit health survey: ${response.statusCode}');
      }
    } catch (e) {
      rethrow;
    }
  }

  // 中医体质辨识
  Future<TcmConstitution> analyzeTcmConstitution(Map<String, dynamic> data) async {
    try {
      final response = await _healthClient.post(
        Uri.parse('${SuokeConfig.healthApiUrl}/tcm/analysis'),
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': SuokeConfig.healthApiKey,
        },
        body: jsonEncode(data),
      );

      if (response.statusCode == 200) {
        return TcmConstitution.fromMap(jsonDecode(response.body));
      } else {
        throw Exception('Failed to analyze TCM constitution: ${response.statusCode}');
      }
    } catch (e) {
      rethrow;
    }
  }

  // 农产品预制服务
  Future<Map<String, dynamic>> getAgriProducts() async {
    try {
      final response = await _agriClient.get(
        Uri.parse('${SuokeConfig.agriApiUrl}/products'),
        headers: {
          'X-API-Key': SuokeConfig.agriApiKey,
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get products: ${response.statusCode}');
      }
    } catch (e) {
      rethrow;
    }
  }

  // 阿里健康服务
  Future<Map<String, dynamic>> getHealthAdvice(String userId) async {
    try {
      final client = _thirdPartyClients['ali_health'];
      final apiConfig = SuokeConfig.thirdPartyApis['ali_health'];
      if (client == null || apiConfig == null) {
        throw Exception('Ali health API not configured');
      }

      final response = await client.get(
        Uri.parse('${apiConfig['url'] ?? ''}/advice/$userId'),
        headers: {
          'X-API-Key': apiConfig['key'] ?? '',
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get health advice: ${response.statusCode}');
      }
    } catch (e) {
      rethrow;
    }
  }

  @override
  void onClose() {
    _healthClient.close();
    _agriClient.close();
    for (final client in _thirdPartyClients.values) {
      client.close();
    }
    super.onClose();
  }
} 