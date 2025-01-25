import 'package:injectable/injectable.dart';
import '../../domain/services/ai_service.dart';
import '../../core/network/network_service.dart';

@Injectable(as: AIService)
class AIServiceImpl implements AIService {
  final NetworkService _network;

  const AIServiceImpl(this._network);

  @override
  Future<String> sendMessage(String message) async {
    final response = await _network.post(
      '/ai/chat',
      {'message': message},
    );
    return response['response'] as String;
  }
} 