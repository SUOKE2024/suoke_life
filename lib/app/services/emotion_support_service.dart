import 'package:get/get.dart';
import 'ai_service.dart';

class EmotionSupportService extends GetxService {
  final AiService _aiService = Get.find();

  Future<Map<String, dynamic>> analyzeEmotion(String text) async {
    try {
      final analysis = await _aiService.queryKnowledge(
        'analyze_emotion',
        parameters: {'text': text},
      );

      return {
        'emotion': analysis['emotion'],
        'intensity': analysis['intensity'],
        'keywords': analysis['keywords'],
      };
    } catch (e) {
      rethrow;
    }
  }

  Future<String> provideEmotionalSupport(Map<String, dynamic> emotionAnalysis) async {
    try {
      final prompt = _buildSupportPrompt(emotionAnalysis);
      return await _aiService.chatWithAssistant(prompt, 'xiaoi');
    } catch (e) {
      return '我理解你的感受,让我们一起面对。';
    }
  }

  String _buildSupportPrompt(Map<String, dynamic> analysis) {
    return '''
    基于以下情感分析结果提供温暖的情感支持:
    - 情绪类型: ${analysis['emotion']}
    - 情绪强度: ${analysis['intensity']}
    - 关键词: ${analysis['keywords'].join('、')}
    
    请给出富有同理心和建设性的回应。
    ''';
  }

  Future<List<String>> suggestActivities(String emotion) async {
    try {
      final prompt = '''
      针对 $emotion 情绪,推荐一些有助于调节心情的活动:
      1. 应该做什么
      2. 不应该做什么
      3. 可以寻求哪些帮助
      ''';
      
      final response = await _aiService.chatWithAssistant(prompt, 'xiaoi');
      return response.split('\n').where((line) => line.isNotEmpty).toList();
    } catch (e) {
      return ['散步', '听音乐', '与朋友聊天'];
    }
  }
} 