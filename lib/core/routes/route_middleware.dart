import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../auth/services/auth_service.dart';
import 'route_paths.dart';

class RouteMiddleware extends GetMiddleware {
  @override
  RouteSettings? redirect(String? route) {
    // 获取当前路由
    final currentRoute = route ?? '';
    
    // 检查是否需要登录
    final needAuth = _needAuthentication(currentRoute);
    final isAuthenticated = AuthService.to.isLoggedIn;
    
    if (needAuth && !isAuthenticated) {
      // 保存尝试访问的路由
      _saveAttemptedRoute(currentRoute);
      // 重定向到登录页
      return const RouteSettings(name: RoutePaths.login);
    }
    
    return null;
  }
  
  bool _needAuthentication(String route) {
    // 不需要登录的路由
    final publicRoutes = [
      RoutePaths.home,
      RoutePaths.login,
      RoutePaths.register,
      RoutePaths.privacy,
      RoutePaths.terms,
      RoutePaths.about,
    ];
    
    return !publicRoutes.contains(route);
  }
  
  void _saveAttemptedRoute(String route) {
    if (route != RoutePaths.login && route != RoutePaths.register) {
      Get.parameters['redirect'] = route;
    }
  }
  
  @override
  GetPage? onPageCalled(GetPage? page) {
    return page;
  }
  
  @override
  List<Bindings>? onBindingsStart(List<Bindings>? bindings) {
    return bindings;
  }
  
  @override
  GetPageBuilder? onPageBuildStart(GetPageBuilder? page) {
    return page;
  }
  
  @override
  Widget onPageBuilt(Widget page) {
    return page;
  }
  
  @override
  void onPageDispose() {
    // 页面销毁时的清理工作
  }
} 