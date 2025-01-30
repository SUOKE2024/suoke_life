import '../../../core/network/network_service.dart';
import '../../../data/models/chat_message.dart';

class ChatService {
  final NetworkService _network;

  ChatService(this._network);

  Future<List<ChatMessage>> getMessages() async {
    final response = await _network.get('/chat/messages');
    return (response.data as List)
        .map((json) => ChatMessage.fromJson(json))
        .toList();
  }

  Future<dynamic> post(String endpoint, {Map<String, dynamic>? data}) async {
    final response = await _network.post(
      endpoint,
      data: data,
      options: null,
    );
    return response;
  }
} 