import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/config/env_config.dart';

class AiAssistantService {
  final String apiKey;
  final String baseUrl = 'https://ark.cn-beijing.volces.com/api/v3';
  final String modelId = 'ep-20241205165226-slv2t';

  AiAssistantService({String? apiKey}) : apiKey = apiKey ?? EnvConfig.doubaoApiKey;

  /// 发送消息到API
  Future<Map<String, dynamic>> sendMessage(List<Map<String, String>> messages) async {
    try {
      final List<Map<String, String>> enhancedMessages = [
        {
          'role': 'system',
          'content': getSystemPrompt(),
        },
        ...messages,
      ];

      final response = await http.post(
        Uri.parse('$baseUrl/chat/completions'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
        },
        body: jsonEncode({
          'messages': enhancedMessages,
          'model': modelId,
          'temperature': 0.7,
          'max_tokens': 800,
        }),
      );

      if (response.statusCode == 200) {
        return {
          'success': true,
          'data': jsonDecode(response.body),
          'message': '发送成功',
        };
      } else {
        return {
          'success': false,
          'error': '请求失败: ${response.statusCode}',
          'message': response.body,
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
        'message': '连接异常',
      };
    }
  }

  /// 测试API连接
  Future<Map<String, dynamic>> testConnection() async {
    return sendMessage([
      {
        'role': 'user',
        'content': '你好，这是一个测试消息。',
      }
    ]);
  }

  /// 处理对话历史
  Future<Map<String, dynamic>> handleConversation(List<Map<String, String>> history, String newMessage) async {
    // 确保历史记录不会太长，保留最近的10条消息
    if (history.length > 10) {
      history = history.sublist(history.length - 10);
    }
    
    // 添加新消息
    history.add({
      'role': 'user',
      'content': newMessage,
    });

    return sendMessage(history);
  }

  /// 处理语音输入
  Future<Map<String, dynamic>> handleVoiceInput(String audioPath) async {
    try {
      // 这里添加语音转文字的处理逻辑
      final response = await http.post(
        Uri.parse('$baseUrl/audio/transcriptions'),
        headers: {
          'Authorization': 'Bearer $apiKey',
          'Content-Type': 'multipart/form-data',
        },
        body: {
          'file': await http.MultipartFile.fromPath('audio', audioPath),
          'model': 'whisper-1',
        },
      );

      if (response.statusCode == 200) {
        return {
          'success': true,
          'data': jsonDecode(response.body),
          'message': '语音识别成功',
        };
      } else {
        return {
          'success': false,
          'error': '语音识别失败: ${response.statusCode}',
          'message': response.body,
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
        'message': '语音处理异常',
      };
    }
  }

  /// 处理视频分析
  Future<Map<String, dynamic>> handleVideoAnalysis(String videoPath) async {
    try {
      // 这里添加视频分析的处理逻辑
      final response = await http.post(
        Uri.parse('$baseUrl/video/analysis'),
        headers: {
          'Authorization': 'Bearer $apiKey',
          'Content-Type': 'multipart/form-data',
        },
        body: {
          'file': await http.MultipartFile.fromPath('video', videoPath),
          'analysis_type': 'all', // 可选：姿态分析、物体识别等
        },
      );

      if (response.statusCode == 200) {
        return {
          'success': true,
          'data': jsonDecode(response.body),
          'message': '视频分析成功',
        };
      } else {
        return {
          'success': false,
          'error': '视频分析失败: ${response.statusCode}',
          'message': response.body,
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
        'message': '视频处理异常',
      };
    }
  }

  /// 获取系统提示
  String getSystemPrompt() {
    return '''你是一个名叫小艾的AI生活助理，请遵循以下原则：

1. 身份和个性：
   - 始终记住你叫"小艾"，是一位贴心的生活助理
   - 保持温暖亲切的语气，适当使用表情符号
   - 对用户的生活问题表示关心和理解

2. 回答规范：
   - 回答要简洁、准确、实用
   - 提供切实可行的生活建议
   - 涉及健康问题时，建议就医并说明原因
   - 不确定的内容要明确说明
   - 时间相关问题要说明无法获取实时时间

3. 对话技巧：
   - 主动询问细节，帮助更好地理解用户需求
   - 保持对话的连贯性和上下文理解
   - 适时提供生活小贴士和建议

4. 特殊说明：
   - 明确表示自己是AI助理，不能执行实体操作
   - 不能获取实时信息（如当前时间、天气等）
   - 健康建议仅供参考，建议就医
   - 注重实用性和可操作性的建议

5. 多模态交互能力：
   - 支持语音输入识别和对话
   - 支持视频分析和场景理解
   - 能够结合语音和视频信息提供更准确的建议
   - 在处理多模态数据时保持耐心和友好''';
  }

  /// 获取支持的功能列表
  Map<String, List<String>> getSupportedFeatures() {
    return {
      '语音交互': [
        '语音识别转文字',
        '语音对话',
        '语音情绪识别',
      ],
      '视频分析': [
        '人物姿态分析',
        '物体识别',
        '场景理解',
        '动作识别',
      ],
      '生活助理': [
        '健康建议',
        '饮食指导',
        '作息建议',
        '生活小贴士',
      ],
      '数据收集': [
        '语音数据采集',
        '视频数据采集',
        '用户习惯分析',
        '健康数据追踪',
      ],
    };
  }
} 