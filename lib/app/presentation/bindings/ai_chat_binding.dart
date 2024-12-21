import 'package:get/get.dart';
import '../controllers/ai/ai_chat_detail_controller.dart';
import '../controllers/ai/ai_chat_history_controller.dart';
import '../controllers/ai/ai_settings_controller.dart';
import '../../services/ai/ai_service.dart';
import '../../services/storage/chat_storage_service.dart';
import '../../services/voice/voice_service.dart';

class AIChatBinding extends Bindings {
  @override
  void dependencies() {
    // 获取必要的服务
    final aiService = Get.find<AIService>();
    final storageService = Get.find<ChatStorageService>();

    // 注册聊天详情控制器
    Get.lazyPut(() => AIChatDetailController(
      aiService,
      storageService,
    ));

    // 注册聊天历史控制器
    Get.lazyPut(() => AIChatHistoryController(
      storageService,
    ));

    // 注册设置控制器
    Get.lazyPut(() => AISettingsController(
      aiService,
      storageService,
    ));

    // 注册聊天控制器
    Get.lazyPut(() => AIChatController(
      Get.find<AIService>(),
      Get.find<ChatStorageService>(),
      Get.find<VoiceService>(),
    ));
  }
} 