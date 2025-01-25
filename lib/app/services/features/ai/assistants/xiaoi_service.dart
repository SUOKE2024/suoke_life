import 'package:injectable/injectable.dart';
import '../../../../core/network/network_service.dart';
import '../base_ai_service.dart';

@injectable
class XiaoiService implements BaseAIService {
  final NetworkService _network;

  XiaoiService(this._network);

  @override
  Future<String> chat(String message) async {
    final response = await _network.post(
      '/ai/xiaoi/chat',
      data: {'message': message},
    );
    return response.data['reply'] as String;
  }

  @override
  Future<bool> handleVoiceInput(String audioPath) async {
    // TODO: 实现语音输入
    return true;
  }

  @override
  Future<String?> generateVoiceOutput(String text) async {
    // TODO: 实现语音合成
    return null;
  }
} 