import 'package:get/get.dart';
import 'package:suoke_app/app/core/di/service_registry.dart';
import 'package:suoke_app/app/core/database/database_helper.dart';
import 'package:suoke_app/app/services/features/chat/chat_service.dart';
import 'package:suoke_app/app/services/features/suoke/suoke_service.dart';

class MockServiceRegistry extends ServiceRegistry {
  final DatabaseHelper databaseHelper;
  final ChatService chatService;
  final SuokeService suokeService;

  MockServiceRegistry({
    required this.databaseHelper,
    required this.chatService,
    required this.suokeService,
  });

  @override
  Future<void> init() async {
    // 先初始化各个服务
    await suokeService.init();
    await chatService.loadMessages();

    // 然后注册到 Get
    Get.put<DatabaseHelper>(databaseHelper, permanent: true);
    Get.put<ChatService>(chatService, permanent: true);
    Get.put<SuokeService>(suokeService, permanent: true);
  }
} 