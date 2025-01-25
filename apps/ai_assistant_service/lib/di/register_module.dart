import 'package:injectable/injectable.dart';
import 'package:suoke_life/core/di/modules/network_module.dart';
import 'package:suoke_life/core/di/modules/storage_module.dart';
import 'package:suoke_life/core/config/app_config.dart';

@InjectableInit(
  initializerName: r'$initGetIt', // default
  preferRelativeImports: true, // default
  asExtension: false, // default
)
void configureDependencies() {
  _configureDependencies();
}

@module
abstract class AiAssistantServiceModule extends NetworkModule with StorageModule {
  // 可以添加特定于 ai_assistant_service 的依赖
}

void _configureDependencies() {
  // 这里可以添加一些初始化逻辑
  getIt<AppConfig>();
  getIt<AgentMemoryService>();
} 