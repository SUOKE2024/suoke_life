import 'package:get/get.dart';
import '../../core/config/assistant_config.dart';
import '../../core/config/doubao_config.dart';
import '../doubao_service.dart';

class AiService extends GetxService {
  final DouBaoService _douBaoService = Get.find();
  
  final assistants = {
    'xiaoai': XiaoAiAssistant(),
    'laoke': LaoKeAssistant(), 
    'xiaoke': XiaoKeAssistant(),
  };

  Future<AiService> init() async {
    await _initializeAssistants();
    return this;
  }

  Future<void> _initializeAssistants() async {
    for (final assistant in assistants.values) {
      await assistant.initialize();
    }
  }

  Future<String> chat(String assistantType, String message) async {
    final assistant = assistants[assistantType];
    if (assistant == null) {
      throw Exception('Assistant not found: $assistantType');
    }
    
    try {
      final response = await assistant.chat(message);
      return response;
    } catch (e) {
      throw Exception('Chat failed: ${e.toString()}');
    }
  }

  Future<Map<String, dynamic>> analyze(String assistantType, String text) async {
    final assistant = assistants[assistantType];
    if (assistant == null) {
      throw Exception('Assistant not found: $assistantType');
    }

    try {
      final analysis = await assistant.analyze(text);
      return analysis;
    } catch (e) {
      throw Exception('Analysis failed: ${e.toString()}');
    }
  }

  Future<List<String>> suggest(String assistantType, Map<String, dynamic> context) async {
    final assistant = assistants[assistantType];
    if (assistant == null) {
      throw Exception('Assistant not found: $assistantType');
    }

    try {
      final suggestions = await assistant.suggest(context);
      return suggestions;
    } catch (e) {
      throw Exception('Suggestion failed: ${e.toString()}');
    }
  }
}

abstract class BaseAssistant {
  Future<void> initialize();
  Future<String> chat(String message);
  Future<Map<String, dynamic>> analyze(String text);
  Future<List<String>> suggest(Map<String, dynamic> context);
}

class XiaoAiAssistant extends BaseAssistant {
  late final String _model;
  late final Map<String, dynamic> _config;

  @override
  Future<void> initialize() async {
    _model = DouBaoConfig.modelEndpoints['xiaoai']!;
    _config = AssistantConfig.xiaoai;
  }

  @override
  Future<String> chat(String message) async {
    // 实现小艾的对话逻辑
    return '';
  }

  @override
  Future<Map<String, dynamic>> analyze(String text) async {
    // 实现小艾的分析逻辑
    return {};
  }

  @override
  Future<List<String>> suggest(Map<String, dynamic> context) async {
    // 实现小艾的建议逻辑
    return [];
  }
}

class LaoKeAssistant extends BaseAssistant {
  late final String _model;
  late final Map<String, dynamic> _config;

  @override
  Future<void> initialize() async {
    _model = DouBaoConfig.modelEndpoints['laoke']!;
    _config = AssistantConfig.laoke;
  }

  @override
  Future<String> chat(String message) async {
    // 实现老克的对话逻辑
    return '';
  }

  @override
  Future<Map<String, dynamic>> analyze(String text) async {
    // 实现老克的分析逻辑
    return {};
  }

  @override
  Future<List<String>> suggest(Map<String, dynamic> context) async {
    // 实现老克的建议逻辑
    return [];
  }
}

class XiaoKeAssistant extends BaseAssistant {
  late final String _model;
  late final Map<String, dynamic> _config;

  @override
  Future<void> initialize() async {
    _model = DouBaoConfig.modelEndpoints['xiaoke']!;
    _config = AssistantConfig.xiaoke;
  }

  @override
  Future<String> chat(String message) async {
    // 实现小克的对话逻辑
    return '';
  }

  @override
  Future<Map<String, dynamic>> analyze(String text) async {
    // 实现小克的分析逻辑
    return {};
  }

  @override
  Future<List<String>> suggest(Map<String, dynamic> context) async {
    // 实现小克的建议逻辑
    return [];
  }
} 