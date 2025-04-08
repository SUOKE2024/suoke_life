import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/app_dashboard.dart';
import '../../data/repositories/dashboard_repository_impl.dart';
import '../../domain/repositories/dashboard_repository.dart';
import '../../domain/usecases/dashboard_usecases.dart';
import '../providers/core_providers.dart';

// 应用桌面仓库Provider
final dashboardRepositoryProvider = Provider<DashboardRepository>((ref) {
  final remoteDataSource = ref.watch(dashboardRemoteDataSourceProvider);
  final localDataSource = ref.watch(dashboardLocalDataSourceProvider);
  return DashboardRepositoryImpl(
    remoteDataSource: remoteDataSource,
    localDataSource: localDataSource,
  );
});

// 应用桌面数据源Provider
final dashboardRemoteDataSourceProvider = Provider<DashboardRemoteDataSource>((ref) {
  final dio = ref.watch(dioProvider);
  return DashboardRemoteDataSourceImpl(dio: dio);
});

final dashboardLocalDataSourceProvider = Provider<DashboardLocalDataSource>((ref) {
  final database = ref.watch(databaseProvider);
  return DashboardLocalDataSourceImpl(database: database);
});

// 应用桌面用例Provider
final getUserDashboardUseCaseProvider = Provider<GetUserDashboardUseCase>((ref) {
  return GetUserDashboardUseCase(repository: ref.watch(dashboardRepositoryProvider));
});

final updateDashboardUseCaseProvider = Provider<UpdateDashboardUseCase>((ref) {
  return UpdateDashboardUseCase(repository: ref.watch(dashboardRepositoryProvider));
});

final addDashboardWidgetUseCaseProvider = Provider<AddDashboardWidgetUseCase>((ref) {
  return AddDashboardWidgetUseCase(repository: ref.watch(dashboardRepositoryProvider));
});

final removeDashboardWidgetUseCaseProvider = Provider<RemoveDashboardWidgetUseCase>((ref) {
  return RemoveDashboardWidgetUseCase(repository: ref.watch(dashboardRepositoryProvider));
});

final getAppCategoriesUseCaseProvider = Provider<GetAppCategoriesUseCase>((ref) {
  return GetAppCategoriesUseCase(repository: ref.watch(dashboardRepositoryProvider));
});

// 控制器状态Provider
final dashboardControllerProvider = StateNotifierProvider<DashboardController, DashboardControllerState>((ref) {
  return DashboardController(
    getUserDashboardUseCase: ref.watch(getUserDashboardUseCaseProvider),
    updateDashboardUseCase: ref.watch(updateDashboardUseCaseProvider),
    addDashboardWidgetUseCase: ref.watch(addDashboardWidgetUseCaseProvider),
    removeDashboardWidgetUseCase: ref.watch(removeDashboardWidgetUseCaseProvider),
    getAppCategoriesUseCase: ref.watch(getAppCategoriesUseCaseProvider),
  );
});

// 暴露的Provider
final appDashboardProvider = Provider<AsyncValue<AppDashboard>>((ref) {
  final controller = ref.watch(dashboardControllerProvider);
  return controller.dashboard;
});

final appCategoriesProvider = Provider<AsyncValue<List<AppCategory>>>((ref) {
  final controller = ref.watch(dashboardControllerProvider);
  return controller.categories;
});

// 控制器状态类
class DashboardControllerState {
  final AsyncValue<AppDashboard> dashboard;
  final AsyncValue<List<AppCategory>> categories;
  final bool isEditMode;

  DashboardControllerState({
    this.dashboard = const AsyncValue.loading(),
    this.categories = const AsyncValue.loading(),
    this.isEditMode = false,
  });

  DashboardControllerState copyWith({
    AsyncValue<AppDashboard>? dashboard,
    AsyncValue<List<AppCategory>>? categories,
    bool? isEditMode,
  }) {
    return DashboardControllerState(
      dashboard: dashboard ?? this.dashboard,
      categories: categories ?? this.categories,
      isEditMode: isEditMode ?? this.isEditMode,
    );
  }
}

// 控制器类
class DashboardController extends StateNotifier<DashboardControllerState> {
  final GetUserDashboardUseCase getUserDashboardUseCase;
  final UpdateDashboardUseCase updateDashboardUseCase;
  final AddDashboardWidgetUseCase addDashboardWidgetUseCase;
  final RemoveDashboardWidgetUseCase removeDashboardWidgetUseCase;
  final GetAppCategoriesUseCase getAppCategoriesUseCase;

  DashboardController({
    required this.getUserDashboardUseCase,
    required this.updateDashboardUseCase,
    required this.addDashboardWidgetUseCase,
    required this.removeDashboardWidgetUseCase,
    required this.getAppCategoriesUseCase,
  }) : super(DashboardControllerState()) {
    loadDashboard();
    loadCategories();
  }

  Future<void> loadDashboard() async {
    final result = await getUserDashboardUseCase();
    result.fold(
      (failure) => state = state.copyWith(
        dashboard: AsyncValue.error(failure, StackTrace.current),
      ),
      (dashboard) => state = state.copyWith(
        dashboard: AsyncValue.data(dashboard),
      ),
    );
  }

  Future<void> loadCategories() async {
    final result = await getAppCategoriesUseCase();
    result.fold(
      (failure) => state = state.copyWith(
        categories: AsyncValue.error(failure, StackTrace.current),
      ),
      (categories) => state = state.copyWith(
        categories: AsyncValue.data(categories),
      ),
    );
  }

  void setEditMode(bool isEditMode) {
    state = state.copyWith(isEditMode: isEditMode);
  }

  Future<void> addWidget(AppWidget widget, {int row = 0, int column = 0}) async {
    final result = await addDashboardWidgetUseCase(widget, row: row, column: column);
    result.fold(
      (failure) => state = state.copyWith(
        dashboard: AsyncValue.error(failure, StackTrace.current),
      ),
      (updatedDashboard) => state = state.copyWith(
        dashboard: AsyncValue.data(updatedDashboard),
      ),
    );
  }

  Future<void> removeWidget(String widgetId) async {
    final result = await removeDashboardWidgetUseCase(widgetId);
    result.fold(
      (failure) => state = state.copyWith(
        dashboard: AsyncValue.error(failure, StackTrace.current),
      ),
      (updatedDashboard) => state = state.copyWith(
        dashboard: AsyncValue.data(updatedDashboard),
      ),
    );
  }

  Future<void> updateDashboard(AppDashboard dashboard) async {
    final result = await updateDashboardUseCase(dashboard);
    result.fold(
      (failure) => state = state.copyWith(
        dashboard: AsyncValue.error(failure, StackTrace.current),
      ),
      (updatedDashboard) => state = state.copyWith(
        dashboard: AsyncValue.data(updatedDashboard),
      ),
    );
  }
} 