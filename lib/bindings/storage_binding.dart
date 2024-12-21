import 'package:get/get.dart';
import 'package:hive/hive.dart';
import '../models/message.dart';
import '../services/storage/chat_storage_service.dart';
import '../services/storage/chat_storage_service_impl.dart';
import '../services/media/media_compression_service.dart';
import '../services/storage/storage_quota_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:dio/dio.dart';
import '../services/storage/upload_manager.dart';
import '../services/storage/cache_manager.dart';

class StorageBinding extends Bindings {
  @override
  void dependencies() async {
    // 初始化Hive
    final messageBox = await Hive.openBox<Message>('messages');
    
    // 注册存储服务
    Get.lazyPut<ChatStorageService>(
      () => ChatStorageServiceImpl(messageBox),
    );

    // 注册媒体压缩服务
    Get.lazyPut(() => MediaCompressionService());

    // 注册存储配额服务
    final prefs = await SharedPreferences.getInstance();
    Get.lazyPut(() => StorageQuotaService(prefs));

    // 注册上传管理器
    final dio = Get.find<Dio>();
    final uploadManager = UploadManager(dio);
    await uploadManager.init();
    Get.lazyPut(() => uploadManager);

    // 注册缓存管理器
    Get.lazyPut(() => CacheManager());
  }
} 