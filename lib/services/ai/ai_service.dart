import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

enum AIModel {
  xiaoKe('ep-20241024122905-r8xsl', 'doubao-pro-32k'),
  xiaoAi('ep-20241207124106-4b5xn', 'doubao-pro-128k'),
  laoKe('ep-20241207124339-rh46z', 'doubao-embedding');

  final String endpoint;
  final String model;

  const AIModel(this.endpoint, this.model);
}

class AIService {
  static final String _baseUrl = 'https://ark.cn-beijing.volces.com/api/v3';
  static final String _apiKey = dotenv.env['DOUBAO_API_KEY'] ?? '92492541-4e14-439e-9831-73b107cca783';
  
  final _dio = Dio(BaseOptions(
    baseUrl: _baseUrl,
    headers: {
      'Authorization': 'Bearer $_apiKey',
      'Content-Type': 'application/json',
    },
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 30),
    validateStatus: (status) {
      return status! < 500;
    },
  ));

  static const String _xiaoKeSystemPrompt = '''
你是小克，一个专注于高效工作的AI助手。
你的主要职责是：
1. 提供工作效率工具
2. 帮助用户管理时间
3. 提供专业的工作建议
4. 帮助用户实现目标

请用专业、友好的语气与用户交流，注重效率和实用性。
''';

  static const String _xiaoAiSystemPrompt = '''
你是一个名叫小艾的AI生活助理，请遵循以下原则：

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
''';

  static const String _laoKeSystemPrompt = '''
你是老克，一个专注于知识分享和学习的AI助手。
你的主要职责是：
1. 解答用户的专业问题
2. 推荐合适的学习资源
3. 分享高效的学习方法
4. 帮助用户构建知识体系

请用专业、友好的语气与用户交流，注重知识的准确性和实用性。
''';

  Future<String> chat({
    required AIModel model,
    required String message,
    String? context,
  }) async {
    try {
      // 如果是 embedding 模型，使用 embeddings 接口
      if (model == AIModel.laoKe) {
        return await getEmbeddings(message);
      }

      String systemPrompt;
      switch (model) {
        case AIModel.xiaoKe:
          systemPrompt = _xiaoKeSystemPrompt;
          break;
        case AIModel.xiaoAi:
          systemPrompt = _xiaoAiSystemPrompt;
          break;
        case AIModel.laoKe:
          systemPrompt = _laoKeSystemPrompt;
          break;
      }
      
      final response = await _dio.post(
        '/chat/completions',
        data: {
          'model': model.model,  // 使用模型名称
          'messages': [
            {'role': 'system', 'content': systemPrompt},
            {'role': 'user', 'content': message},
          ],
          'stream': false,
          'temperature': 0.7,
          'max_tokens': 4096,
        },
      );

      if (response.statusCode == 200 && response.data != null) {
        final content = response.data['choices'][0]['message']['content'];
        return content ?? '抱歉，我没有理解您的问题。';
      }
      
      throw Exception('API调用失败: ${response.statusCode}');
    } catch (e) {
      print('Error details: $e');
      throw Exception('AI服务异常: $e');
    }
  }

  Future<String> getEmbeddings(String input) async {
    try {
      final response = await _dio.post(
        '/embeddings',
        data: {
          'model': AIModel.laoKe.model,
          'input': [input],
        },
      );

      if (response.statusCode == 200 && response.data != null) {
        // 处理 embeddings 响应
        final embeddings = response.data['data'][0]['embedding'];
        return embeddings.toString();
      }

      throw Exception('嵌入请求失败: ${response.statusCode}');
    } catch (e) {
      print('Error details: $e');
      throw Exception('嵌入服务异常: $e');
    }
  }
}
