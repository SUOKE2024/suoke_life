import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// 应用路由观察者
/// 
/// 用于记录页面访问数据和管理页面级别的生命周期
class AppRouteObserver extends AutoRouterObserver {
  final Ref? ref;
  
  AppRouteObserver({this.ref});
  
  @override
  void didPush(Route route, Route? previousRoute) {
    _logRouteEvent('PUSH', route, previousRoute);
    
    // 可以在这里触发页面访问分析事件
    if (ref != null && route.settings.name != null) {
      // 例如：ref.read(analyticsProvider).logPageView(route.settings.name!);
    }
  }

  @override
  void didPop(Route route, Route? previousRoute) {
    _logRouteEvent('POP', route, previousRoute);
  }

  @override
  void didRemove(Route route, Route? previousRoute) {
    _logRouteEvent('REMOVE', route, previousRoute);
  }

  @override
  void didReplace({Route? newRoute, Route? oldRoute}) {
    _logRouteEvent('REPLACE', newRoute, oldRoute);
  }

  @override
  void didInitTabRoute(TabPageRoute route, TabPageRoute? previousRoute) {
    _logRouteEvent('TAB INIT', route as Route?, previousRoute as Route?);
  }

  @override
  void didChangeTabRoute(TabPageRoute route, TabPageRoute previousRoute) {
    _logRouteEvent('TAB CHANGE', route as Route?, previousRoute as Route?);
  }

  void _logRouteEvent(String event, Route? route, Route? previousRoute) {
    // 仅在调试模式下输出路由日志
    assert(() {
      print('路由事件: $event | '
          '当前: ${route?.settings.name} | '
          '来源: ${previousRoute?.settings.name}');
      return true;
    }());
  }
}

/// 路由观察者提供者
final routeObserverProvider = Provider<AppRouteObserver>((ref) {
  return AppRouteObserver(ref: ref);
}); 