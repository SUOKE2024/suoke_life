import 'package:get/get.dart';
import '../config/env_config.dart';
import '../../services/storage_service.dart';
import '../../services/chat_service.dart';
import '../../services/doubao_service.dart';
import '../../services/voice_service.dart';

class DependencyInjection {
  static Future<void> init() async {
    // 环境配置
    await Get.putAsync(() => EnvConfig().init());

    // 存储服务
    await Get.putAsync(() => StorageService().init());

    // 语音服务
    await Get.putAsync(() => VoiceService().init());

    // 豆包服务
    Get.lazyPut(() => DouBaoService());

    // 聊天服务 - 不需要异步初始化
    Get.lazyPut(() => ChatService());
  }
} 