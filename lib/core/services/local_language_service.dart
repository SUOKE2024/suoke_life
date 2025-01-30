import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'ai_service.dart';

class LocalLanguageService extends GetxService {
  final StorageService _storageService = Get.find();
  final AiService _aiService = Get.find();

  // 识别方言
  Future<Map<String, dynamic>> detectDialect(String text) async {
    try {
      // 使用 AI 分析方言特征
      final analysis = await _aiService.queryKnowledge(
        'analyze_dialect',
        parameters: {'text': text},
      );

      return {
        'dialect': analysis['dialect'],
        'confidence': analysis['confidence'],
        'region': analysis['region'],
        'features': analysis['features'],
      };
    } catch (e) {
      rethrow;
    }
  }

  // 方言转换
  Future<String> translateDialect(String text, String targetDialect) async {
    try {
      // 识别原方言
      final detection = await detectDialect(text);
      
      // 使用 AI 进行转换
      final response = await _aiService.chatWithAssistant(
        'translate_to_$targetDialect: $text',
        'xiaoi',
      );

      return response;
    } catch (e) {
      rethrow;
    }
  }

  // 获取方言特征库
  Future<Map<String, dynamic>> getDialectFeatures(String dialect) async {
    try {
      final data = await _storageService.getLocal('dialect_features_$dialect');
      return data != null ? Map<String, dynamic>.from(data) : {};
    } catch (e) {
      return {};
    }
  }

  // 更新方言特征库
  Future<void> updateDialectFeatures(String dialect, Map<String, dynamic> features) async {
    try {
      await _storageService.saveLocal('dialect_features_$dialect', features);
    } catch (e) {
      rethrow;
    }
  }
} 