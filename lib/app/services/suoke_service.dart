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

  @override
  void onInit() {
    super.onInit();
    // 初始化第三方 API 客户端
    for (final api in SuokeConfig.thirdPartyApis.keys) {
      _thirdPartyClients[api] = http.Client();
    }
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
        return HealthSurvey.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Failed to submit survey: ${response.statusCode}');
      }
    } catch (e) {
      rethrow;
    }
  }

  // 体质检测服务
  Future<TCMConstitution> checkTCMConstitution(Map<String, dynamic> data) async {
    try {
      final client = _thirdPartyClients['tcm_diagnosis'];
      final apiConfig = SuokeConfig.thirdPartyApis['tcm_diagnosis']!;

      final response = await client!.post(
        Uri.parse('${apiConfig['url']}/constitution/check'),
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiConfig['key'],
        },
        body: jsonEncode(data),
      );

      if (response.statusCode == 200) {
        return TCMConstitution.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Failed to check constitution: ${response.statusCode}');
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
      final apiConfig = SuokeConfig.thirdPartyApis['ali_health']!;

      final response = await client!.get(
        Uri.parse('${apiConfig['url']}/advice/$userId'),
        headers: {
          'X-API-Key': apiConfig['key'],
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