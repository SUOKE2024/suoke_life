import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../services/connectivity_service.dart';
import '../routes/app_pages.dart';

class NetworkMiddleware extends GetMiddleware {
  @override
  int? get priority => 2;

  @override
  RouteSettings? redirect(String? route) {
    final connectivityService = Get.find<ConnectivityService>();
    
    // 检查网络连接
    if (!connectivityService.hasConnection) {
      // 如果是必须在线的页面，则重定向到离线提示页面
      if (_requiresNetwork(route)) {
        return const RouteSettings(name: Routes.OFFLINE);
      }
    }
    
    return null;
  }

  bool _requiresNetwork(String? route) {
    // 定义需要网络连接的页面列表
    const networkRequiredRoutes = [
      Routes.SYNC_SETTINGS,
      Routes.AI_CHAT,
      Routes.EXPLORE,
      Routes.FEEDBACK,
    ];
    
    return networkRequiredRoutes.contains(route);
  }

  @override
  GetPage? onPageCalled(GetPage? page) {
    return page;
  }

  @override
  Widget onPageBuilt(Widget page) {
    return page;
  }

  @override
  void onPageDispose() {
    // ��面销毁时的清理工作
  }
} 