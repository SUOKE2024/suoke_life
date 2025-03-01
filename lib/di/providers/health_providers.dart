import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logger/logger.dart';

import '../../data/datasources/health_data_source.dart';
import '../../data/datasources/local/database_helper.dart';
import '../../data/datasources/local/health_data_local_source.dart';
import '../../data/datasources/remote/health_data_remote_source.dart';
import '../../data/repositories/health_repository_impl.dart';
import '../../domain/entities/health_data.dart';
import '../../domain/repositories/health_repository.dart';
import '../../domain/usecases/health/delete_health_data_usecase.dart';
import '../../domain/usecases/health/get_daily_health_summary_usecase.dart';
import '../../domain/usecases/health/get_health_data_by_id_usecase.dart';
import '../../domain/usecases/health/get_health_data_by_type_usecase.dart';
import '../../domain/usecases/health/get_health_statistics_usecase.dart';
import '../../domain/usecases/health/get_health_suggestions_usecase.dart';
import '../../domain/usecases/health/get_health_trend_usecase.dart';
import '../../domain/usecases/health/get_latest_health_data_usecase.dart';
import '../../domain/usecases/health/get_user_health_data_usecase.dart';
import '../../domain/usecases/health/get_user_health_score_usecase.dart';
import '../../domain/usecases/health/save_health_data_usecase.dart';
import '../../domain/usecases/health/sync_external_health_data_usecase.dart';
import '../../domain/usecases/health/update_health_data_usecase.dart';
import 'core_providers.dart';

/// 健康数据本地数据源Provider
final healthDataLocalSourceProvider = Provider<HealthDataSource>((ref) {
  final databaseHelper = ref.watch(databaseHelperProvider);
  final logger = ref.watch(loggerProvider);
  
  return HealthDataLocalSource(
    databaseHelper: databaseHelper,
    logger: logger,
  );
});

/// 健康数据远程数据源Provider
final healthDataRemoteSourceProvider = Provider<HealthDataSource>((ref) {
  final dio = ref.watch(dioProvider);
  final logger = ref.watch(loggerProvider);
  
  return HealthDataRemoteSource(
    dio: dio,
    logger: logger,
  );
});

/// 健康数据仓库Provider
final healthRepositoryProvider = Provider<HealthRepository>((ref) {
  final remoteDataSource = ref.watch(healthDataRemoteSourceProvider);
  final localDataSource = ref.watch(healthDataLocalSourceProvider);
  final logger = ref.watch(loggerProvider);
  
  return HealthRepositoryImpl(
    remoteDataSource: remoteDataSource,
    localDataSource: localDataSource,
    logger: logger,
  );
});

/// 获取用户健康数据用例Provider
final getUserHealthDataUseCaseProvider = Provider<GetUserHealthDataUseCase>((ref) {
  final repository = ref.watch(healthRepositoryProvider);
  return GetUserHealthDataUseCase(repository);
});

/// 获取特定类型健康数据用例Provider
final getHealthDataByTypeUseCaseProvider = Provider<GetHealthDataByTypeUseCase>((ref) {
  final repository = ref.watch(healthRepositoryProvider);
  return GetHealthDataByTypeUseCase(repository);
});

/// 获取健康数据详情用例Provider
final getHealthDataByIdUseCaseProvider = Provider<GetHealthDataByIdUseCase>((ref) {
  final repository = ref.watch(healthRepositoryProvider);
  return GetHealthDataByIdUseCase(repository);
});

/// 保存健康数据用例Provider
final saveHealthDataUseCaseProvider = Provider<SaveHealthDataUseCase>((ref) {
  final repository = ref.watch(healthRepositoryProvider);
  return SaveHealthDataUseCase(repository);
});

/// 更新健康数据用例Provider
final updateHealthDataUseCaseProvider = Provider<UpdateHealthDataUseCase>((ref) {
  final repository = ref.watch(healthRepositoryProvider);
  return UpdateHealthDataUseCase(repository);
});

/// 删除健康数据用例Provider
final deleteHealthDataUseCaseProvider = Provider<DeleteHealthDataUseCase>((ref) {
  final repository = ref.watch(healthRepositoryProvider);
  return DeleteHealthDataUseCase(repository);
});

/// 获取每日健康汇总用例Provider
final getDailyHealthSummaryUseCaseProvider = Provider<GetDailyHealthSummaryUseCase>((ref) {
  final repository = ref.watch(healthRepositoryProvider);
  return GetDailyHealthSummaryUseCase(repository);
});

/// 获取健康数据统计用例Provider
final getHealthStatisticsUseCaseProvider = Provider<GetHealthStatisticsUseCase>((ref) {
  final repository = ref.watch(healthRepositoryProvider);
  return GetHealthStatisticsUseCase(repository);
});

/// 获取最新健康数据用例Provider
final getLatestHealthDataUseCaseProvider = Provider<GetLatestHealthDataUseCase>((ref) {
  final repository = ref.watch(healthRepositoryProvider);
  return GetLatestHealthDataUseCase(repository);
});

/// 获取健康趋势用例Provider
final getHealthTrendUseCaseProvider = Provider<GetHealthTrendUseCase>((ref) {
  final repository = ref.watch(healthRepositoryProvider);
  return GetHealthTrendUseCase(repository);
});

/// 同步外部健康数据用例Provider
final syncExternalHealthDataUseCaseProvider = Provider<SyncExternalHealthDataUseCase>((ref) {
  final repository = ref.watch(healthRepositoryProvider);
  return SyncExternalHealthDataUseCase(repository);
});

/// 获取用户健康评分用例Provider
final getUserHealthScoreUseCaseProvider = Provider<GetUserHealthScoreUseCase>((ref) {
  final repository = ref.watch(healthRepositoryProvider);
  return GetUserHealthScoreUseCase(repository);
});

/// 获取健康建议用例Provider
final getHealthSuggestionsUseCaseProvider = Provider<GetHealthSuggestionsUseCase>((ref) {
  final repository = ref.watch(healthRepositoryProvider);
  return GetHealthSuggestionsUseCase(repository);
});

/// 用户健康数据状态Provider
final userHealthDataStateProvider = StateNotifierProvider.family<UserHealthDataNotifier, AsyncValue<List<HealthData>>, String>(
  (ref, userId) => UserHealthDataNotifier(
    getUserHealthDataUseCase: ref.watch(getUserHealthDataUseCaseProvider),
    userId: userId,
  ),
);

/// 用户健康数据状态管理器
class UserHealthDataNotifier extends StateNotifier<AsyncValue<List<HealthData>>> {
  final GetUserHealthDataUseCase _getUserHealthDataUseCase;
  final String _userId;
  
  UserHealthDataNotifier({
    required GetUserHealthDataUseCase getUserHealthDataUseCase,
    required String userId,
  })  : _getUserHealthDataUseCase = getUserHealthDataUseCase,
        _userId = userId,
        super(const AsyncValue.loading()) {
    loadHealthData();
  }
  
  /// 加载用户健康数据
  Future<void> loadHealthData({
    DateTime? startDate,
    DateTime? endDate,
    int limit = 100,
    int offset = 0,
  }) async {
    try {
      state = const AsyncValue.loading();
      final healthData = await _getUserHealthDataUseCase.execute(
        _userId,
        startDate: startDate,
        endDate: endDate,
        limit: limit,
        offset: offset,
      );
      state = AsyncValue.data(healthData);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }
  
  /// 添加健康数据
  Future<void> addHealthData(HealthData data) async {
    try {
      // 更新本地状态
      final currentData = state.value ?? [];
      state = AsyncValue.data([data, ...currentData]);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }
  
  /// 更新健康数据
  Future<void> updateHealthData(HealthData data) async {
    try {
      // 更新本地状态
      final currentData = state.value ?? [];
      final updatedData = currentData.map((item) => item.id == data.id ? data : item).toList();
      state = AsyncValue.data(updatedData);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }
  
  /// 删除健康数据
  Future<void> removeHealthData(String dataId) async {
    try {
      // 更新本地状态
      final currentData = state.value ?? [];
      final updatedData = currentData.where((item) => item.id != dataId).toList();
      state = AsyncValue.data(updatedData);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }
}

/// 特定类型健康数据状态Provider
final healthDataByTypeStateProvider = StateNotifierProvider.family<HealthDataByTypeNotifier, AsyncValue<List<HealthData>>, HealthDataTypeParam>(
  (ref, param) => HealthDataByTypeNotifier(
    getHealthDataByTypeUseCase: ref.watch(getHealthDataByTypeUseCaseProvider),
    userId: param.userId,
    type: param.type,
  ),
);

/// 健康数据类型参数
class HealthDataTypeParam {
  final String userId;
  final HealthDataType type;
  
  HealthDataTypeParam({
    required this.userId,
    required this.type,
  });
  
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is HealthDataTypeParam &&
          runtimeType == other.runtimeType &&
          userId == other.userId &&
          type == other.type;
  
  @override
  int get hashCode => userId.hashCode ^ type.hashCode;
}

/// 特定类型健康数据状态管理器
class HealthDataByTypeNotifier extends StateNotifier<AsyncValue<List<HealthData>>> {
  final GetHealthDataByTypeUseCase _getHealthDataByTypeUseCase;
  final String _userId;
  final HealthDataType _type;
  
  HealthDataByTypeNotifier({
    required GetHealthDataByTypeUseCase getHealthDataByTypeUseCase,
    required String userId,
    required HealthDataType type,
  })  : _getHealthDataByTypeUseCase = getHealthDataByTypeUseCase,
        _userId = userId,
        _type = type,
        super(const AsyncValue.loading()) {
    loadHealthData();
  }
  
  /// 加载特定类型健康数据
  Future<void> loadHealthData({
    DateTime? startDate,
    DateTime? endDate,
    int limit = 100,
    int offset = 0,
  }) async {
    try {
      state = const AsyncValue.loading();
      final healthData = await _getHealthDataByTypeUseCase.execute(
        _userId,
        _type,
        startDate: startDate,
        endDate: endDate,
        limit: limit,
        offset: offset,
      );
      state = AsyncValue.data(healthData);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }
  
  /// 添加健康数据
  Future<void> addHealthData(HealthData data) async {
    try {
      // 确保数据类型匹配
      if (data.type != _type) return;
      
      // 更新本地状态
      final currentData = state.value ?? [];
      state = AsyncValue.data([data, ...currentData]);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }
  
  /// 更新健康数据
  Future<void> updateHealthData(HealthData data) async {
    try {
      // 确保数据类型匹配
      if (data.type != _type) return;
      
      // 更新本地状态
      final currentData = state.value ?? [];
      final updatedData = currentData.map((item) => item.id == data.id ? data : item).toList();
      state = AsyncValue.data(updatedData);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }
  
  /// 删除健康数据
  Future<void> removeHealthData(String dataId) async {
    try {
      // 更新本地状态
      final currentData = state.value ?? [];
      final updatedData = currentData.where((item) => item.id != dataId).toList();
      state = AsyncValue.data(updatedData);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }
}

/// 每日健康汇总状态Provider
final dailyHealthSummaryProvider = FutureProvider.family<Map<HealthDataType, num>, DailyHealthSummaryParam>(
  (ref, param) async {
    final useCase = ref.watch(getDailyHealthSummaryUseCaseProvider);
    return useCase.execute(param.userId, param.date);
  },
);

/// 每日健康汇总参数
class DailyHealthSummaryParam {
  final String userId;
  final DateTime date;
  
  DailyHealthSummaryParam({
    required this.userId,
    required this.date,
  });
  
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is DailyHealthSummaryParam &&
          runtimeType == other.runtimeType &&
          userId == other.userId &&
          date.year == other.date.year &&
          date.month == other.date.month &&
          date.day == other.date.day;
  
  @override
  int get hashCode => userId.hashCode ^ date.year.hashCode ^ date.month.hashCode ^ date.day.hashCode;
}

/// 健康趋势状态Provider
final healthTrendProvider = FutureProvider.family<List<Map<String, dynamic>>, HealthTrendParam>(
  (ref, param) async {
    final useCase = ref.watch(getHealthTrendUseCaseProvider);
    return useCase.execute(
      param.userId,
      param.type,
      startDate: param.startDate,
      endDate: param.endDate,
      interval: param.interval,
    );
  },
);

/// 健康趋势参数
class HealthTrendParam {
  final String userId;
  final HealthDataType type;
  final DateTime startDate;
  final DateTime endDate;
  final String interval;
  
  HealthTrendParam({
    required this.userId,
    required this.type,
    required this.startDate,
    required this.endDate,
    required this.interval,
  });
  
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is HealthTrendParam &&
          runtimeType == other.runtimeType &&
          userId == other.userId &&
          type == other.type &&
          startDate == other.startDate &&
          endDate == other.endDate &&
          interval == other.interval;
  
  @override
  int get hashCode =>
      userId.hashCode ^
      type.hashCode ^
      startDate.hashCode ^
      endDate.hashCode ^
      interval.hashCode;
}

/// 用户健康评分状态Provider
final userHealthScoreProvider = FutureProvider.family<Map<String, dynamic>, String>(
  (ref, userId) async {
    final useCase = ref.watch(getUserHealthScoreUseCaseProvider);
    return useCase.execute(userId);
  },
);

/// 健康建议状态Provider
final healthSuggestionsProvider = FutureProvider.family<List<String>, HealthSuggestionsParam>(
  (ref, param) async {
    final useCase = ref.watch(getHealthSuggestionsUseCaseProvider);
    return useCase.execute(param.userId, focusArea: param.focusArea);
  },
);

/// 健康建议参数
class HealthSuggestionsParam {
  final String userId;
  final HealthDataType? focusArea;
  
  HealthSuggestionsParam({
    required this.userId,
    this.focusArea,
  });
  
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is HealthSuggestionsParam &&
          runtimeType == other.runtimeType &&
          userId == other.userId &&
          focusArea == other.focusArea;
  
  @override
  int get hashCode => userId.hashCode ^ (focusArea?.hashCode ?? 0);
} 