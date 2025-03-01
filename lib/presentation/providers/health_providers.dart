import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/health_service.dart';
import '../../domain/repositories/health_repository.dart';
import '../../data/repositories/health_repository_impl.dart';
import '../../core/network/api_client.dart';
import '../../di/providers.dart';

/// 健康服务存储库提供者
final healthRepositoryProvider = Provider<HealthRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return HealthRepositoryImpl(apiClient: apiClient);
});

/// 健康服务列表状态
class HealthServicesState {
  final List<HealthService> services;
  final bool isLoading;
  final String? error;
  
  const HealthServicesState({
    this.services = const [],
    this.isLoading = false,
    this.error,
  });
  
  HealthServicesState copyWith({
    List<HealthService>? services,
    bool? isLoading,
    String? error,
  }) {
    return HealthServicesState(
      services: services ?? this.services,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// 健康服务列表通知者
class HealthServicesNotifier extends StateNotifier<HealthServicesState> {
  final HealthRepository _repository;
  
  HealthServicesNotifier(this._repository) : super(const HealthServicesState());
  
  /// 加载所有健康服务
  Future<void> loadServices() async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final services = await _repository.getAllServices();
      state = state.copyWith(
        services: services,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '加载健康服务失败: $e',
      );
    }
  }
  
  /// 按类型筛选服务
  Future<void> filterServicesByType(String type) async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final services = await _repository.getServicesByType(type);
      state = state.copyWith(
        services: services,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '筛选服务失败: $e',
      );
    }
  }
  
  /// 搜索服务
  Future<void> searchServices(String query) async {
    if (query.isEmpty) {
      loadServices();
      return;
    }
    
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final services = await _repository.searchServices(query);
      state = state.copyWith(
        services: services,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '搜索服务失败: $e',
      );
    }
  }
  
  /// 按价格范围筛选服务
  Future<void> filterServicesByPriceRange(double minPrice, double maxPrice) async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final services = await _repository.getServicesByPriceRange(minPrice, maxPrice);
      state = state.copyWith(
        services: services,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '按价格筛选服务失败: $e',
      );
    }
  }
}

/// 健康服务列表提供者
final healthServicesProvider = StateNotifierProvider<HealthServicesNotifier, HealthServicesState>((ref) {
  final repository = ref.watch(healthRepositoryProvider);
  return HealthServicesNotifier(repository);
});

/// 精选健康服务提供者
final featuredServicesProvider = FutureProvider<List<HealthService>>((ref) async {
  final repository = ref.watch(healthRepositoryProvider);
  return repository.getFeaturedServices();
});

/// 最近使用的健康服务提供者
final recentlyUsedServicesProvider = FutureProvider<List<HealthService>>((ref) async {
  final repository = ref.watch(healthRepositoryProvider);
  return repository.getRecentlyUsedServices();
});

/// 健康服务类别提供者
final serviceTypesProvider = FutureProvider<List<String>>((ref) async {
  final repository = ref.watch(healthRepositoryProvider);
  return repository.getServiceTypes();
});

/// 健康服务详情状态
class HealthServiceDetailState {
  final HealthService? service;
  final bool isLoading;
  final String? error;
  
  const HealthServiceDetailState({
    this.service,
    this.isLoading = false,
    this.error,
  });
  
  HealthServiceDetailState copyWith({
    HealthService? service,
    bool? isLoading,
    String? error,
  }) {
    return HealthServiceDetailState(
      service: service ?? this.service,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// 健康服务详情通知者
class HealthServiceDetailNotifier extends StateNotifier<HealthServiceDetailState> {
  final HealthRepository _repository;
  
  HealthServiceDetailNotifier(this._repository) : super(const HealthServiceDetailState());
  
  /// 加载服务详情
  Future<void> loadServiceDetail(String serviceId) async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final service = await _repository.getServiceById(serviceId);
      state = state.copyWith(
        service: service,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '加载服务详情失败: $e',
      );
    }
  }
}

/// 健康服务详情提供者
final healthServiceDetailProvider = StateNotifierProvider<HealthServiceDetailNotifier, HealthServiceDetailState>((ref) {
  final repository = ref.watch(healthRepositoryProvider);
  return HealthServiceDetailNotifier(repository);
});