import 'package:get/get.dart';

class TestEnv extends GetxService {
  Future<TestEnv> init() async {
    return this;
  }

  // 测试环境配置
  String get doubaoApiKey => 'test_api_key';
  String get doubaoApiUrl => 'https://test.api.doubao.com';
  String get doubaoPro32kEp => 'test-ep-32k';
  String get doubaoPro128kEp => 'test-ep-128k';
  String get doubaoEmbeddingEp => 'test-ep-embedding';
} 