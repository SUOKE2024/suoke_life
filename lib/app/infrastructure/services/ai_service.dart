import 'dart:ffi';
import 'dart:io';
import 'package:path/path.dart' as path;

class AIService {
  static const String _apiKey = '92492541-4e14-439e-9831-73b107cca783';
  static const String _baseUrl = 'https://ark.cn-beijing.volces.com/api/v3';

  Future<String> getAIResponse(String message,
      {String model = 'ep-20241024122905-r8xsl'}) async {
    // 使用 Process.run 调用 Python 脚本
    final scriptPath =
        path.join(Directory.current.path, 'scripts', 'ai_service.py');

    final result = await Process.run('python3', [
      scriptPath,
      '--api_key',
      _apiKey,
      '--base_url',
      _baseUrl,
      '--model',
      model,
      '--message',
      message,
    ]);

    if (result.exitCode != 0) {
      throw Exception('AI service error: ${result.stderr}');
    }

    return result.stdout.toString().trim();
  }
}
