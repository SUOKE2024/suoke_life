import 'package:get/get.dart';
import '../database/database_helper.dart';
import '../../services/features/chat/chat_service.dart';
import '../../services/features/suoke/suoke_service.dart';

abstract class ServiceRegistry {
  Future<void> init();
}

class ServiceRegistryImpl implements ServiceRegistry {
  @override
  Future<void> init() async {
    // 注册数据库
    final databaseHelper = DatabaseHelper();
    Get.put<DatabaseHelper>(databaseHelper, permanent: true);

    // 注册 SuokeService
    final suokeService = SuokeServiceImpl();
    Get.put<SuokeService>(suokeService, permanent: true);

    // 注册 ChatService
    final chatService = ChatService();
    Get.put<ChatService>(chatService, permanent: true);

    // 初始化服务
    await suokeService.init();
    await chatService.loadMessages();
  }
} 