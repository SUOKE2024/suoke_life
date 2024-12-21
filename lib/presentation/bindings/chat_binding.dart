import 'package:get/get.dart';
import '../controllers/chat/chat_detail_controller.dart';
import '../controllers/chat/chat_settings_controller.dart';
import '../controllers/chat/chat_history_controller.dart';
import '../../services/ai/ai_service.dart';
import '../../services/storage/chat_storage_service.dart';
import '../../services/chat/chat_settings_service.dart';

class ChatBinding extends Bindings {
  @override
  void dependencies() {
    // 服务
    final aiService = Get.find<AIService>();
    final storageService = Get.find<ChatStorageService>();
    final settingsService = Get.find<ChatSettingsService>();

    // 控制器
    Get.lazyPut(() => ChatDetailController(
      aiService,
      storageService,
      'assets/images/ai/xiaoke.png',
    ));
    
    Get.lazyPut(() => ChatSettingsController(settingsService));
    Get.lazyPut(() => ChatHistoryController(storageService));
  }
} 