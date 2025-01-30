// Remove all imports and code related to 'injectable'

class AIServiceImpl {
  final NetworkService _network;

  const AIServiceImpl(this._network);

  Future<String> sendMessage(String message) async {
    final response = await _network.post(
      '/ai/chat',
      {'message': message},
    );
    return response['response'] as String;
  }
} 