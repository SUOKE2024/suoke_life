import 'package:get/get.dart';
import 'package:shared_preferences.dart';
import '../core/network/api_client.dart';
import '../core/utils/token_manager.dart';
import '../services/auth_service.dart';
import '../services/user_service.dart';
import '../services/message_service.dart';
import '../services/session_manager_service.dart';

class InitialBinding extends Bindings {
  @override
  void dependencies() async {
    // 初始化 SharedPreferences
    final prefs = await SharedPreferences.getInstance();
    Get.put(prefs);

    // 初始化 TokenManager
    final tokenManager = TokenManager(Get.find<SharedPreferences>());
    Get.put(tokenManager);

    // 初始化 ApiClient
    final apiClient = ApiClient(tokenManager: Get.find());
    Get.put(apiClient);

    // 初始化各种服务
    Get.put(AuthService(
      apiClient: Get.find(),
      tokenManager: Get.find(),
    ));
    Get.put(UserService(apiClient: Get.find()));
    Get.put(MessageService(apiClient: Get.find()));
    Get.put(SessionManagerService());
  }
} 