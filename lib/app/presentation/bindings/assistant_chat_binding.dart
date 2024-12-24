import 'package:get/get.dart';
import '../controllers/assistant_chat_controller.dart';

class AssistantChatBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => AssistantChatController());
  }
} 