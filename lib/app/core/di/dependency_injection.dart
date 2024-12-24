import 'package:get/get.dart';
import '../config/env_config.dart';
import '../storage/storage_service.dart';
import '../../services/chat_service.dart';
import '../../services/doubao_service.dart';
import '../../services/voice_service.dart';
import '../database/database_helper.dart';
import '../../services/ai/ai_service.dart';

class DependencyInjection {
  static Future<void> init() async {
    // 环境配置
    await Get.putAsync(() => EnvConfig().init());

    // 初始化数据库和存储服务
    await Get.putAsync(() async {
      final service = StorageService();
      await service.init();
      return service;
    });

    // 语音服务
    await Get.putAsync(() => VoiceService().init());

    // 豆包服务
    Get.lazyPut(() => DouBaoService());

    // AI 服务
    Get.lazyPut(() => AiService(douBaoService: Get.find<DouBaoService>()));

    // 聊天服务
    Get.lazyPut(() => ChatService());
  }
} 