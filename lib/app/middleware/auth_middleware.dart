import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../services/auth_service.dart';
import '../routes/app_routes.dart';

class AuthMiddleware extends GetMiddleware {
  @override
  int? get priority => 1;

  @override
  RouteSettings? redirect(String? route) {
    final authService = Get.find<AuthService>();
    
    if (!authService.isAuthenticated.value && 
        route != Routes.LOGIN && 
        route != Routes.REGISTER && 
        route != Routes.RESET_PASSWORD) {
      return const RouteSettings(name: Routes.LOGIN);
    }
    
    if (authService.isAuthenticated.value && 
        (route == Routes.LOGIN || route == Routes.REGISTER)) {
      return const RouteSettings(name: Routes.MAIN);
    }
    
    return null;
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