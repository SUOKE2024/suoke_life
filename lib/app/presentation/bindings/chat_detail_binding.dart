import 'package:get/get.dart';
import '../controllers/chat/chat_detail_controller.dart';
import '../../services/features/chat/chat_service.dart';

class ChatDetailBinding extends Bindings {
  @override
  void dependencies() {
    final roomId = Get.parameters['id'] ?? '';
    Get.lazyPut<ChatDetailController>(
      () => ChatDetailController(Get.find<ChatService>(), roomId),
    );
  }
} 