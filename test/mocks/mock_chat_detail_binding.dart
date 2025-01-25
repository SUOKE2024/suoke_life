import 'package:get/get.dart';
import 'package:suoke_app/app/presentation/controllers/chat_detail_controller.dart';
import 'package:suoke_app/app/services/features/chat/chat_service.dart';
import 'mock_chat_service.dart';

class MockChatDetailBinding extends Bindings {
  final ChatService chatService;

  MockChatDetailBinding({required this.chatService});

  @override
  void dependencies() {
    Get.put<ChatService>(chatService, permanent: true);
    
    Get.lazyPut<ChatDetailController>(
      () => ChatDetailController(
        chatService: Get.find<ChatService>(),
      ),
      fenix: true,
    );
  }
} 