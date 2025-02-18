import '../../../core/network/network_service.dart';

class AIService {
  final NetworkService _network;

  AIService(this._network);

  Future<Map<String, dynamic>> chat(String message) async {
    final response = await _network.post(
      '/ai/chat',
      data: {'message': message},
    );
    return response.data;
  }
} 