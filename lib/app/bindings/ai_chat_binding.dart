import 'package:get/get.dart';
import '../core/services/ai_service.dart';
import '../presentation/controllers/ai_chat_controller.dart';

class AIChatBinding extends Bindings {
  @override
  void dependencies() {
    // 获取路由参数中的 AI ID
    final aiId = Get.parameters['id'] ?? '';
    
    // 注入 AI 服务
    Get.lazyPut<AIService>(() => AIService(
      apiClient: Get.find(),
    ));
    
    // 注入 AI 聊天控制器
    Get.lazyPut<AIChatController>(() => AIChatController(
      aiService: Get.find(),
      aiId: aiId,
    ));
  }
} 