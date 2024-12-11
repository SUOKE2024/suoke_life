import 'dart:convert';
import 'package:http/http.dart' as http;

class CozeService {
  final String _baseUrl = 'https://www.coze.cn/api/v1';
  final String _botId;
  final String _token;

  CozeService({
    required String botId,
    required String token,
  })  : _botId = botId,
        _token = token;

  Future<String> sendMessage(String message) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/chat/completions'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $_token',
        },
        body: jsonEncode({
          'bot_id': _botId,
          'messages': [
            {
              'role': 'user',
              'content': message,
            }
          ],
          'stream': false,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['choices'][0]['message']['content'];
      } else {
        throw Exception('Failed to get response: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error sending message: $e');
    }
  }
} 