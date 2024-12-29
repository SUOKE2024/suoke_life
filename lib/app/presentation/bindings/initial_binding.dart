import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import '../services/logging_service.dart';
import '../services/privacy_service.dart';
import '../services/encryption_service.dart';
import '../services/network_service.dart';
import '../services/auth_service.dart';
import '../services/ai_service.dart';
import '../services/ai/services/doubao_service.dart';
import '../services/settings_service.dart';
import '../services/analytics_service.dart';
import '../services/suoke_service.dart';
import '../presentation/controllers/home/home_controller.dart';
import '../presentation/controllers/chat/chat_controller.dart';
import '../presentation/controllers/suoke/suoke_controller.dart';
import '../presentation/controllers/explore/explore_controller.dart';
import '../presentation/controllers/life/life_controller.dart';
import '../presentation/controllers/settings/settings_controller.dart';

class InitialBinding extends Bindings {
  @override
  Future<void> dependencies() async {
    // 基础服务 - 按依赖顺序注入
    final storageService = await Get.putAsync(() => StorageService().init());
    Get.put(LoggingService());
    Get.put(PrivacyService());
    Get.put(EncryptionService());
    Get.put(NetworkService());
    Get.put(AuthService());
    
    // AI相关服务 - 确保正确的注入顺序
    final doubaoService = Get.put(DouBaoService());
    Get.put(AiService());
    
    // 其他服务
    Get.put(SettingsService());
    Get.put(AnalyticsService());
    
    // 业务服务
    Get.put(SuokeService(storageService: storageService));
    
    // 先注入 HomeController，让它��责管理其他控制器
    Get.put(HomeController(), permanent: true);
    
    // 其他控制器会由 HomeController 在需要时注入
    Get.put(SettingsController());
  }
} 