// 路由提供者文件
// 定义路由相关的Provider

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/router/app_router.dart';
import '../providers/auth_providers.dart';
import 'package:suoke_life/domain/repositories/auth_repository.dart';

/// 路由观察者提供者
final routeObserverProvider = Provider<AppRouteObserver>((ref) {
  return AppRouteObserver();
});

/// 路由守卫提供者
final authGuardProvider = Provider<AuthGuard>((ref) {
  final authRepository = ref.watch(authRepositoryProvider);
  return AuthGuard(authRepository);
});

/// 应用路由提供者
final appRouterProvider = Provider<AppRouter>((ref) {
  final authGuard = ref.watch(authGuardProvider);
  return AppRouter(authGuard: authGuard);
}); 