import 'package:get/get.dart';
import 'package:shared_preferences.dart';
import '../core/network/api_client.dart';
import '../core/utils/token_manager.dart';
import '../services/auth_service.dart';
import '../services/user_service.dart';
import '../services/message_service.dart';
import '../services/session_manager_service.dart';
import '../services/storage_service.dart';
import '../services/network_service.dart';
import '../services/ai_service.dart';
import '../services/settings_service.dart';
import '../services/analytics_service.dart';

class InitialBinding extends Bindings {
  @override
  void dependencies() {
    // 核心服务
    Get.put(StorageService());
    Get.put(NetworkService());
    Get.put(AuthService());
    
    // AI服务
    Get.put(AiService());
    
    // 其他基础服务
    Get.put(SettingsService());
    Get.put(AnalyticsService());
  }
} 