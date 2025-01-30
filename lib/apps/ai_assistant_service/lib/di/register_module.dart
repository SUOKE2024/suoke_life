import 'package:suoke_life/lib/core/di/modules/network_module.dart';
import 'package:suoke_life/lib/core/di/modules/storage_module.dart';
import 'package:suoke_life/lib/core/config/app_config.dart';

@module
abstract class AiAssistantServiceModule extends NetworkModule with StorageModule {
  // 可以添加特定于 ai_assistant_service 的依赖
}

void _configureDependencies() {
  // 这里可以添加一些初始化逻辑
  getIt<AppConfig>();
  getIt<AgentMemoryService>();
} 