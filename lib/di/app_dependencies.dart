import 'package:core/core.dart';
import 'package:explore/explore.dart';
import 'package:auth/auth.dart';
import 'package:get_it/get_it.dart';

class AppDependencies {
  static final getIt = GetIt.instance;

  static void setup() {
    // 初始化核心服务
    setupCoreDependencies(getIt);

    // 初始化认证模块
    setupAuthDependencies(getIt);

    // 初始化首页模块
    setupHomeDependencies(getIt);

    // 初始化生活模块
    setupLifeDependencies(getIt);

    // 初始化个人资料模块
    setupProfileDependencies(getIt);

    // 初始化用户模块
    setupUserDependencies(getIt);

    // 初始化suoke模块
    setupSuokeDependencies(getIt);

    // 初始化探索模块
    setupExploreDependencies(getIt);

    // 初始化其他模块...
  }

  static void setupSuokeDependencies(GetIt getIt) {
    SuokeDependencies.setup(getIt);
  }

  static void setupUserDependencies(GetIt getIt) {
    UserDependencies.setup(getIt);
  }

  static void setupProfileDependencies(GetIt getIt) {
    ProfileDependencies.setup(getIt);
  }

  static void setupLifeDependencies(GetIt getIt) {
    LifeDependencies.setup(getIt);
  }

  static void setupHomeDependencies(GetIt getIt) {
    HomeDependencies.setup(getIt);
  }

  static void setupAuthDependencies(GetIt getIt) {
    AuthDependencies.setup(getIt);
  }

  static void setupCoreDependencies(GetIt getIt) {
    // 配置Dio实例并添加日志拦截器
    final dio = Dio()
      ..interceptors.add(LogInterceptor(
        request: true,
        requestBody: true,
        responseBody: true,
        requestHeader: true,
        responseHeader: false,
      ));

    // 注册增强版网络服务
    getIt.registerLazySingleton<NetworkService>(
      () => DioNetworkService(dio),
    );

    // 注册AI服务
    getIt.registerLazySingleton<AIService>(
      () => AIServiceImpl(apiClient: getIt<NetworkService>()),
    );

    // 注册内容审核服务
    getIt.registerLazySingleton<ContentModerationService>(
      () => ContentModerationServiceImpl(
        aiService: getIt<AIService>(),
        networkService: getIt<NetworkService>(),
      ),
    );
  }

  static void setupSuokeDependencies(GetIt getIt) {
    // 注册SUOKE模块用例
    getIt.registerLazySingleton<GetServicesUseCase>(
      () => GetServicesUseCaseImpl(getIt<NetworkService>())
    );

    // 注册服务卡片状态管理
    getIt.registerFactory(() => ServiceCardState(
      getServicesUseCase: getIt<GetServicesUseCase>(),
      moderationService: getIt<ContentModerationService>(),
    ));
  }
}
