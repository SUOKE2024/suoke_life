import 'package:flutter/foundation.dart';
import '../../../models/chat_message.dart';
import '../../../services/ai/ai_service.dart';

class XiaoiService {
  final AIService _aiService;
  
  static const String name = '小艾';
  static const String description = '您的贴心生活助理，专注于健康咨询和情感支持';
  
  static const String _systemPrompt = '''
你是小艾,一个专业的AI健康助手。你的主要职责包括：

1. 健康数据收集与分析
- 收集用户的健康数据（如症状、生活习惯等）
- 分析用户的健康状况
- 追踪用户的健康趋势

2. 健康建议提供
- 提供科学的健康建议
- 推荐健康的生活方式
- 建议合适的运动方案
- 提供饮食营养指导

3. 健康知识普及
- 解答健康相关问题
- 普及医学知识
- 纠正健康误区
- 提供可靠的健康资讯

4. 风险评估与提醒
- 评估健康风险
- 提供预防建议
- 及时提醒就医
- 推荐合适的专科医生

注意事项：
1. 使用专业但易懂的语言
2. 给出具体可行的建议
3. 涉及专业医疗问题时，建议就医
4. 保持友善、耐心的沟通态度
5. 确保建议的安全性和可靠性

免责���明：
我提供的建议仅供参考，不能替代专业医生的诊断和治疗。如有严重健康问题，请及时就医。
''';

  XiaoiService(this._aiService);

  // 处理用户消息
  Future<ChatMessage> processMessage(ChatMessage userMessage) async {
    try {
      // 调用豆包API获取回复
      final response = await _aiService.chat(
        model: AIModel.xiaoAi,
        message: userMessage.content,
        context: _systemPrompt,
      );
      
      // 返回助手消息
      return ChatMessage.assistant(
        content: response,
      );
    } catch (e) {
      debugPrint('Xiaoi failed to process message: $e');
      return ChatMessage.error(
        content: '消息处理失败: $e',
      );
    }
  }
} 