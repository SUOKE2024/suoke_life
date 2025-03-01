import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/health_service.dart';

/// 健康服务状态
class HealthServiceState {
  final List<HealthService> allServices;
  final List<HealthService> featuredServices;
  final List<HealthService> recentlyUsedServices;
  final bool isLoading;
  final String? error;

  HealthServiceState({
    required this.allServices,
    required this.featuredServices,
    required this.recentlyUsedServices,
    this.isLoading = false,
    this.error,
  });

  HealthServiceState copyWith({
    List<HealthService>? allServices,
    List<HealthService>? featuredServices,
    List<HealthService>? recentlyUsedServices,
    bool? isLoading,
    String? error,
  }) {
    return HealthServiceState(
      allServices: allServices ?? this.allServices,
      featuredServices: featuredServices ?? this.featuredServices,
      recentlyUsedServices: recentlyUsedServices ?? this.recentlyUsedServices,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// 健康服务状态管理器
class HealthServiceNotifier extends StateNotifier<HealthServiceState> {
  HealthServiceNotifier()
      : super(
          HealthServiceState(
            allServices: [],
            featuredServices: [],
            recentlyUsedServices: [],
            isLoading: true,
          ),
        ) {
    _loadServices();
  }

  /// 加载健康服务
  Future<void> _loadServices() async {
    try {
      // 模拟网络延迟
      await Future.delayed(const Duration(milliseconds: 800));

      // 获取预设服务列表
      final services = HealthService.presetServices;

      // 推荐服务（免费服务）
      final featuredServices = services.where((service) => !service.isPremium).toList();

      // 最近使用的服务（示例数据）
      final recentlyUsedServices = [
        services.firstWhere((s) => s.id == 'tcm_diagnosis'),
        services.firstWhere((s) => s.id == 'health_assessment'),
      ];

      // 更新状态
      state = state.copyWith(
        allServices: services,
        featuredServices: featuredServices,
        recentlyUsedServices: recentlyUsedServices,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        error: e.toString(),
        isLoading: false,
      );
    }
  }

  /// 按类型过滤健康服务
  List<HealthService> filterServicesByType(HealthServiceType type) {
    return state.allServices.where((service) => service.type == type).toList();
  }

  /// 按价格过滤健康服务
  List<HealthService> filterServicesByPrice({required bool isPremium}) {
    return state.allServices.where((service) => service.isPremium == isPremium).toList();
  }

  /// 搜索健康服务
  List<HealthService> searchServices(String query) {
    final lowercaseQuery = query.toLowerCase();
    return state.allServices.where((service) {
      return service.name.toLowerCase().contains(lowercaseQuery) ||
          service.description.toLowerCase().contains(lowercaseQuery) ||
          service.tags.any((tag) => tag.toLowerCase().contains(lowercaseQuery));
    }).toList();
  }

  /// 记录服务使用
  void recordServiceUsage(HealthService service) {
    // 移除之前的记录（如果存在）
    final updatedRecentlyUsed = state.recentlyUsedServices
        .where((s) => s.id != service.id)
        .toList();

    // 添加到最近使用列表的最前面
    updatedRecentlyUsed.insert(0, service);

    // 限制最近使用列表长度为5
    if (updatedRecentlyUsed.length > 5) {
      updatedRecentlyUsed.removeLast();
    }

    // 更新状态
    state = state.copyWith(
      recentlyUsedServices: updatedRecentlyUsed,
    );
  }
}

/// 全局健康服务状态提供者
final healthServiceProvider = StateNotifierProvider<HealthServiceNotifier, HealthServiceState>((ref) {
  return HealthServiceNotifier();
}); 