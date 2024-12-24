import 'package:get/get.dart';
import '../core/config/app_config.dart';
import 'doubao_service.dart';

class AiService extends GetxService {
  final assistants = {
    'xiaoai': XiaoAiAssistant(),
    'laoke': LaoKeAssistant(),
    'xiaoke': XiaoKeAssistant(),
  };

  Future<String> chat(String assistantId, String message) async {
    final assistant = assistants[assistantId];
    if (assistant == null) return '';
    return assistant.chat(message);
  }
} 