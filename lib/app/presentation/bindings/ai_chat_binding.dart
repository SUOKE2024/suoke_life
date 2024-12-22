import 'package:get/get.dart';
import '../controllers/ai_chat_controller.dart';
import '../../services/chat_service.dart';
import '../../services/doubao_service.dart';
import '../../services/voice_service.dart';

class AiChatBinding implements Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => ChatService());
    Get.lazyPut(() => DouBaoService());
    Get.lazyPut(() => VoiceService());
    Get.lazyPut(() => AiChatController());
  }
} 