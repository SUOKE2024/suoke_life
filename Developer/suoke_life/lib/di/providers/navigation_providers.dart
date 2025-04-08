import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/datasources/remote/navigation_remote_datasource.dart';
import '../../data/repositories/navigation_repository_impl.dart';
import '../../domain/repositories/navigation_repository.dart';
import '../../domain/usecases/navigation/analyze_environment_usecase.dart';
import '../../domain/usecases/navigation/get_navigation_usecase.dart';
import '../../core/network/api_client.dart';
import '../../domain/entities/navigation_guidance.dart';

/// 导航服务API客户端Provider
final navigationApiClientProvider = Provider<ApiClient>((ref) {
  final baseApiClient = ref.read(apiClientProvider);
  return ApiClient(
    baseUrl: baseApiClient.baseUrl,
    dio: baseApiClient.dio,
    endpoint: '/api/v1/navigation',
  );
});

/// 导航远程数据源Provider
final navigationRemoteDataSourceProvider = Provider<NavigationRemoteDataSource>((ref) {
  final apiClient = ref.read(navigationApiClientProvider);
  return NavigationRemoteDataSourceImpl(apiClient: apiClient);
});

/// 导航仓库Provider
final navigationRepositoryProvider = Provider<NavigationRepository>((ref) {
  final remoteDataSource = ref.read(navigationRemoteDataSourceProvider);
  return NavigationRepositoryImpl(
    remoteDataSource: remoteDataSource,
  );
});

/// 环境分析用例Provider
final analyzeEnvironmentUseCaseProvider = Provider<AnalyzeEnvironmentUseCase>((ref) {
  final repository = ref.read(navigationRepositoryProvider);
  return AnalyzeEnvironmentUseCase(repository: repository);
});

/// 获取导航用例Provider
final getNavigationUseCaseProvider = Provider<GetNavigationUseCase>((ref) {
  final repository = ref.read(navigationRepositoryProvider);
  return GetNavigationUseCase(repository: repository);
});

/// 导航服务Provider
final navigationServiceProvider = Provider<NavigationService>((ref) {
  final analyzeEnvironmentUseCase = ref.read(analyzeEnvironmentUseCaseProvider);
  final getNavigationUseCase = ref.read(getNavigationUseCaseProvider);
  
  return NavigationService(
    analyzeEnvironmentUseCase: analyzeEnvironmentUseCase,
    getNavigationUseCase: getNavigationUseCase,
  );
});

/// 导航服务
class NavigationService {
  final AnalyzeEnvironmentUseCase analyzeEnvironmentUseCase;
  final GetNavigationUseCase getNavigationUseCase;
  
  NavigationService({
    required this.analyzeEnvironmentUseCase,
    required this.getNavigationUseCase,
  });
  
  /// 分析环境
  Future<NavigationGuidance> analyzeEnvironment({
    required Map<String, dynamic> location,
    required String imageData,
    Map<String, dynamic>? contextInfo,
  }) async {
    return await analyzeEnvironmentUseCase.execute(
      location: location,
      imageData: imageData,
      contextInfo: contextInfo,
    );
  }
  
  /// 获取导航建议
  Future<NavigationGuidance> getNavigation({
    required Map<String, dynamic> location,
    required Map<String, dynamic> destination,
    Map<String, dynamic>? preferences,
    Map<String, dynamic>? environmentData,
  }) async {
    return await getNavigationUseCase.execute(
      location: location,
      destination: destination,
      preferences: preferences,
      environmentData: environmentData,
    );
  }
}