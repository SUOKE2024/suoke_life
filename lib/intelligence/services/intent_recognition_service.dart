import '../models/intent.dart';
import '../models/conversation_context.dart';

class IntentRecognitionService {
  // 意图模式匹配规则
  final Map<String, List<String>> _patterns = {
    Intent.TASK_EXECUTION: [
      '执行',
      '运行',
      '启动',
      '打开',
      '关闭',
      '停止',
    ],
    Intent.INFORMATION_QUERY: [
      '什么',
      '为什么',
      '怎么',
      '如何',
      '查询',
      '搜索',
      '告诉我',
    ],
    Intent.SYSTEM_CONTROL: [
      '设置',
      '配置',
      '调整',
      '更改',
      '修改',
      '系统',
    ],
  };

  // 提取意图参数的规则
  final Map<String, Map<String, RegExp>> _parameterPatterns = {
    Intent.TASK_EXECUTION: {
      'action': RegExp(r'(执行|运行|启动|打开|关闭|停止)'),
      'target': RegExp(r'(?<=(?:执行|运行|启动|打开|关闭|停止))[^，。！？]*'),
    },
    Intent.INFORMATION_QUERY: {
      'queryType': RegExp(r'(什么|为什么|怎么|如何)'),
      'queryTarget': RegExp(r'(?<=(?:什么|为什么|怎么|如何))[^，。！？]*'),
    },
    Intent.SYSTEM_CONTROL: {
      'setting': RegExp(r'(?<=(?:设置|配置|调整|更改|修改))[^，。！？]*'),
      'value': RegExp(r'(?<=为|到)[^，。！？]*'),
    },
  };

  Intent recognizeIntent(String input, ConversationContext context) {
    // 1. 检查是否匹配特定意图模式
    for (final entry in _patterns.entries) {
      final intentType = entry.key;
      final patterns = entry.value;
      
      for (final pattern in patterns) {
        if (input.contains(pattern)) {
          // 2. 提取参数
          final parameters = _extractParameters(input, intentType);
          
          // 3. 计算置信度
          final confidence = _calculateConfidence(input, intentType, context);
          
          return Intent(
            type: intentType,
            parameters: parameters,
            confidence: confidence,
          );
        }
      }
    }
    
    // 4. 如果没有匹配到特定意图，返回通用对话意图
    return Intent(
      type: Intent.GENERAL_CHAT,
      confidence: 0.6,
    );
  }

  Map<String, dynamic> _extractParameters(String input, String intentType) {
    final parameters = <String, dynamic>{};
    
    final patterns = _parameterPatterns[intentType];
    if (patterns != null) {
      patterns.forEach((paramName, pattern) {
        final match = pattern.firstMatch(input);
        if (match != null) {
          parameters[paramName] = match.group(0)?.trim();
        }
      });
    }
    
    return parameters;
  }

  double _calculateConfidence(
    String input,
    String intentType,
    ConversationContext context,
  ) {
    double confidence = 0.7; // 基础置信度
    
    // 1. 根据匹配的关键词数量调整置信度
    final patterns = _patterns[intentType] ?? [];
    int matchCount = 0;
    for (final pattern in patterns) {
      if (input.contains(pattern)) matchCount++;
    }
    confidence += (matchCount * 0.1).clamp(0.0, 0.2);
    
    // 2. 根据参数完整性调整置信度
    final parameters = _extractParameters(input, intentType);
    final paramPatterns = _parameterPatterns[intentType] ?? {};
    if (parameters.length == paramPatterns.length) {
      confidence += 0.1;
    }
    
    // 3. 根据上下文连贯性调整置信度
    if (context.messages.isNotEmpty) {
      final lastMessage = context.messages.last;
      if (lastMessage.role == 'assistant' && 
          input.contains(lastMessage.content.split('：').last)) {
        confidence += 0.1;
      }
    }
    
    return confidence.clamp(0.0, 1.0);
  }
} 