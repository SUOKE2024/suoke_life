import 'package:get/get.dart';
import '../controllers/chat/chat_controller.dart';
import '../../services/features/suoke/suoke_service.dart';

class ChatBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<ChatController>(
      () => ChatController(Get.find<SuokeService>()),
    );
  }
} 