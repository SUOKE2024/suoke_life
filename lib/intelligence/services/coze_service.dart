import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/message.dart';

class CozeService {
  final String _botId;
  final String _apiKey;
  final String _baseUrl;
  
  CozeService({
    required String botId,
    required String apiKey,
    String baseUrl = 'https://www.coze.cn/api/bot',
  })  : _botId = botId,
        _apiKey = apiKey,
        _baseUrl = baseUrl;
  
  Future<String> chat(List<Message> messages) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/$_botId/chat'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $_apiKey',
        },
        body: jsonEncode({
          'messages': messages.map((m) => {
            'role': m.role,
            'content': m.content,
          }).toList(),
        }),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['response'] as String;
      } else {
        throw Exception('Coze API error: ${response.statusCode}');
      }
    } catch (e) {
      print('Error calling Coze API: $e');
      return '抱歉，我现在无法连接到服务器，请稍后再试。';
    }
  }
  
  Future<Map<String, dynamic>> analyze(String text) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/$_botId/analyze'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $_apiKey',
        },
        body: jsonEncode({
          'text': text,
        }),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw Exception('Coze API error: ${response.statusCode}');
      }
    } catch (e) {
      print('Error calling Coze API: $e');
      return {};
    }
  }
} 