import 'package:get/get.dart';
import '../services/voice/voice_service.dart';
import '../services/media/image_picker_service.dart';
import '../services/media/video_service.dart';
import '../services/notification/notification_service.dart';
import '../services/storage/storage_quota_service.dart';
import '../services/api/api_service.dart';
import '../services/auth/auth_service.dart';
import '../services/ai/ai_service.dart';

class ServiceBinding extends Bindings {
  @override
  void dependencies() async {
    // 存储配额服务
    final quotaService = Get.find<StorageQuotaService>();

    // 认证服务
    Get.put(AuthService());

    // 语音服务
    final voiceService = VoiceService();
    await voiceService.init();
    Get.lazyPut(() => voiceService);

    // 图片选择服务
    Get.lazyPut(() => ImagePickerService(quotaService));

    // 视频服务
    Get.lazyPut(() => VideoService(quotaService));

    // 通知服务
    final notificationService = NotificationService();
    await notificationService.init();
    Get.lazyPut(() => notificationService);

    Get.lazyPut(() => ApiService());

    // AI 服���
    Get.lazyPut<AIService>(() => AIServiceImpl(
      baseUrl: 'https://api.suoke.life/v1',
      apiKey: const String.fromEnvironment('AI_API_KEY'),
    ));

    // Add to dependencies() method:
    Get.lazyPut(() => VoiceService()..init());
  }
} 