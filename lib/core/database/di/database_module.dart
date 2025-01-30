import 'package:get_it/get_it.dart';
import '../local/config/database_config.dart';

/// 数据库模块依赖注入
void registerDatabaseModule(GetIt getIt) {
  // 注册数据库配置
  getIt.registerLazySingleton<DatabaseConfig>(() => DatabaseConfig.instance);

  // 注册 DAO
  // TODO: 在这里注册具体的 DAO 实现
  // 例如：getIt.registerLazySingleton<UserDao>(() => UserDaoImpl(getIt()));

  // 注册仓库
  // TODO: 在这里注册具体的仓库实现
  // 例如：getIt.registerLazySingleton<UserRepository>(() => UserRepositoryImpl(getIt()));
} 