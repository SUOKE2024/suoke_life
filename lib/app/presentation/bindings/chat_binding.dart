import 'package:get/get.dart';
import '../controllers/chat_detail_controller.dart';
import '../../services/chat_service.dart';
import '../../services/voice_service.dart';

class ChatBinding extends Bindings {
  @override
  void dependencies() {
    // 确保服务已注入
    if (!Get.isRegistered<ChatService>()) {
      Get.put(ChatService());
    }
    if (!Get.isRegistered<VoiceService>()) {
      Get.put(VoiceService());
    }
    
    // 注入控制器
    Get.lazyPut(() => ChatDetailController());
  }
} 