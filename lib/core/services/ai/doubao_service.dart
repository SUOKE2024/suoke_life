// import 'package:injectable/injectable.dart';
import 'base_ai_service.dart';
import 'package:logger/logger.dart';

class DoubaoService extends BaseAiService {
  final Logger _logger = Logger();

  DoubaoService(super.network);

  Future<String> chat({
    required String prompt,
    String model = 'ep-20241024122905-r8xsl', // 小克
  }) async {
    _logger.i('Sending chat request with prompt: $prompt');
    final response = await post('/chat/completions', data: {
      'model': model,
      'messages': [
        {
          'role': 'system',
          'content': '你是豆包，是由字节跳动开发的 AI 人工智能助手',
        },
        {
          'role': 'user',
          'content': prompt,
        },
      ],
    });
    _logger.i('Received chat response: ${response['choices'][0]['message']['content']}');
    return response['choices'][0]['message']['content'];
  }

  Stream<String> chatStream({
    required String prompt,
    String model = 'ep-20241212093835-bl92q', // 小艾
  }) async* {
    _logger.i('Starting chat stream with prompt: $prompt');
    final response = await post('/chat/completions', data: {
      'model': model,
      'messages': [
        {
          'role': 'system',
          'content': '你是豆包，是由字节跳动开发的 AI 人工智能助手',
        },
        {
          'role': 'user',
          'content': prompt,
        },
      ],
      'stream': true,
    });

    for (var chunk in response['chunks']) {
      if (chunk['choices']?.isNotEmpty == true) {
        _logger.i('Received chat stream chunk: ${chunk['choices'][0]['delta']['content']}');
        yield chunk['choices'][0]['delta']['content'];
      }
    }
  }
} 