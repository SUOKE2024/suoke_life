import 'package:injectable/injectable.dart';

@singleton
class AIConfig {
  final String apiKey;
  static const defaultBaseUrl = 'https://ark.cn-beijing.volces.com/api/v3';
  final String baseUrl;
  final Map<String, Map<String, dynamic>> modelConfigs;

  AIConfig({
    required this.apiKey,
    this.baseUrl = defaultBaseUrl,
  }) : modelConfigs = {
    'xiao_ai': {
      'model_id': 'ep-20241212093835-bl92q',
      'system_prompt': '你是小艾，一个友好的AI助手，专注于提供生活和工作建议。',
      'max_tokens': 4000,
      'temperature': 0.8,
      'top_p': 0.95,
    },
    'xiao_ke': {
      'model_id': 'ep-20241024122905-r8xsl',
      'system_prompt': '你是小克，一个专业的农业和健康顾问。',
      'max_tokens': 4000,
      'temperature': 0.7,
      'top_p': 0.95,
    },
    'lao_ke': {
      'model_id': 'ep-20241207124339-rh46z',
      'system_prompt': '你是老克，一个专注于知识分析的AI助手。',
      'max_tokens': 4000,
      'temperature': 0.5,
      'top_p': 0.95,
    },
  };

  String getModelId(String modelType) {
    final config = modelConfigs[modelType];
    if (config == null) {
      throw Exception('Invalid model type: $modelType');
    }
    return config['model_id'] as String;
  }

  String getSystemPrompt(String modelType) {
    final config = modelConfigs[modelType];
    if (config == null) {
      throw Exception('Invalid model type: $modelType');
    }
    return config['system_prompt'] as String;
  }

  Map<String, dynamic> getModelConfig(String modelType) {
    final config = modelConfigs[modelType];
    if (config == null) {
      throw Exception('Invalid model type: $modelType');
    }
    return config;
  }
} 