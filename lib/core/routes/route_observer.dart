import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../logging/app_logger.dart';
import 'route_analytics.dart';

class AppRouteObserver extends NavigatorObserver {
  static final AppRouteObserver _instance = AppRouteObserver._internal();
  static AppRouteObserver get instance => _instance;
  
  AppRouteObserver._internal();
  
  final _routeStack = <Route>[];
  final _routeTimestamps = <Route, DateTime>{};
  
  Route? get currentRoute => _routeStack.isNotEmpty ? _routeStack.last : null;
  String? get currentRouteName => currentRoute?.settings.name;
  List<Route> get routeStack => List.unmodifiable(_routeStack);
  
  @override
  void didPush(Route<dynamic> route, Route<dynamic>? previousRoute) {
    _routeStack.add(route);
    _routeTimestamps[route] = DateTime.now();
    _logRouteChange('PUSH', route, previousRoute);
    _analyzeRouteMetrics(route, previousRoute);
    
    final routeName = route.settings.name;
    final previousRouteName = previousRoute?.settings.name;
    if (routeName != null) {
      RouteAnalytics.to.recordPageView(routeName);
      if (previousRouteName != null) {
        RouteAnalytics.to.recordTransition(previousRouteName, routeName);
      }
    }
  }
  
  @override
  void didPop(Route<dynamic> route, Route<dynamic>? previousRoute) {
    if (_routeStack.isNotEmpty) {
      _routeStack.removeLast();
    }
    final duration = _calculateRouteDuration(route);
    _logRouteChange('POP', route, previousRoute, duration: duration);
    
    final routeName = route.settings.name;
    if (routeName != null && duration != null) {
      RouteAnalytics.to.recordPageDuration(routeName, duration);
    }
    
    _routeTimestamps.remove(route);
  }
  
  @override
  void didReplace({Route<dynamic>? newRoute, Route<dynamic>? oldRoute}) {
    if (oldRoute != null && _routeStack.isNotEmpty) {
      final index = _routeStack.indexOf(oldRoute);
      if (index != -1 && newRoute != null) {
        _routeStack[index] = newRoute;
        _routeTimestamps[newRoute] = DateTime.now();
        
        final duration = _calculateRouteDuration(oldRoute);
        final oldRouteName = oldRoute.settings.name;
        final newRouteName = newRoute.settings.name;
        
        if (oldRouteName != null && duration != null) {
          RouteAnalytics.to.recordPageDuration(oldRouteName, duration);
        }
        
        if (newRouteName != null) {
          RouteAnalytics.to.recordPageView(newRouteName);
          if (oldRouteName != null) {
            RouteAnalytics.to.recordTransition(oldRouteName, newRouteName);
          }
        }
      }
    }
    _logRouteChange('REPLACE', newRoute, oldRoute);
  }
  
  @override
  void didRemove(Route<dynamic> route, Route<dynamic>? previousRoute) {
    _routeStack.remove(route);
    _logRouteChange('REMOVE', route, previousRoute);
    
    final duration = _calculateRouteDuration(route);
    final routeName = route.settings.name;
    if (routeName != null && duration != null) {
      RouteAnalytics.to.recordPageDuration(routeName, duration);
    }
    
    _routeTimestamps.remove(route);
  }
  
  Duration? _calculateRouteDuration(Route route) {
    final startTime = _routeTimestamps[route];
    if (startTime != null) {
      return DateTime.now().difference(startTime);
    }
    return null;
  }
  
  void _logRouteChange(
    String action,
    Route? currentRoute,
    Route? previousRoute, {
    Duration? duration,
  }) {
    final current = currentRoute?.settings.name ?? 'unknown';
    final previous = previousRoute?.settings.name ?? 'unknown';
    final durationStr = duration != null ? ' (duration: ${duration.inSeconds}s)' : '';
    
    AppLogger.instance.info(
      'Route $action: $previous -> $current$durationStr',
      tags: ['ROUTE'],
    );
  }
  
  void _analyzeRouteMetrics(Route route, Route? previousRoute) {
    final routeName = route.settings.name;
    if (routeName == null) return;
    
    // 分析路由深度
    final depth = _routeStack.length;
    if (depth > 10) {
      AppLogger.instance.warning(
        '路由栈深度过大: $depth',
        tags: ['ROUTE', 'PERFORMANCE'],
      );
    }
    
    // 分析路由循环
    final routeNames = _routeStack
        .map((r) => r.settings.name)
        .where((name) => name != null)
        .toList();
    final duplicates = routeNames.where((name) => 
        routeNames.where((n) => n == name).length > 1
    ).toSet();
    
    if (duplicates.isNotEmpty) {
      AppLogger.instance.warning(
        '检测到路由循环: $duplicates',
        tags: ['ROUTE', 'PERFORMANCE'],
      );
    }
  }
  
  // 获取路由历史
  List<String> getRouteHistory() {
    return _routeStack
        .map((route) => route.settings.name ?? 'unknown')
        .toList();
  }
  
  // 获取当前路由深度
  int getRouteDepth() {
    return _routeStack.length;
  }
  
  // 检查是否可以返回
  bool canGoBack() {
    return _routeStack.length > 1;
  }
  
  // 获取上一个路由
  String? getPreviousRouteName() {
    if (_routeStack.length < 2) return null;
    return _routeStack[_routeStack.length - 2].settings.name;
  }
  
  // 清除路由历史
  void clearRouteStack() {
    _routeStack.clear();
    _routeTimestamps.clear();
  }
} 