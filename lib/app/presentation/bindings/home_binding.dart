import 'package:get/get.dart';
import '../controllers/home_controller.dart';
import '../../services/chat_service.dart';

class HomeBinding extends Bindings {
  @override
  void dependencies() {
    // 确保 ChatService 已注入
    if (!Get.isRegistered<ChatService>()) {
      Get.put(ChatService());
    }
    
    // 注入 HomeController
    Get.put(HomeController());
  }
} 