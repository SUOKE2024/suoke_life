import 'package:flutter/material.dart';
import 'package:get/get.dart';

class RouteTransitions {
  // 默认转场动画
  static GetPageRoute defaultTransition(
    Widget page, {
    RouteSettings? settings,
    bool popGesture = true,
  }) {
    return GetPageRoute(
      page: () => page,
      settings: settings,
      popGesture: popGesture,
      transition: Transition.cupertino,
      curve: Curves.easeInOut,
      transitionDuration: const Duration(milliseconds: 300),
    );
  }
  
  // 渐隐渐现动画
  static GetPageRoute fadeTransition(
    Widget page, {
    RouteSettings? settings,
    bool popGesture = true,
  }) {
    return GetPageRoute(
      page: () => page,
      settings: settings,
      popGesture: popGesture,
      transition: Transition.fade,
      curve: Curves.easeInOut,
      transitionDuration: const Duration(milliseconds: 300),
    );
  }
  
  // 缩放动画
  static GetPageRoute scaleTransition(
    Widget page, {
    RouteSettings? settings,
    bool popGesture = true,
  }) {
    return GetPageRoute(
      page: () => page,
      settings: settings,
      popGesture: popGesture,
      transition: Transition.zoom,
      curve: Curves.easeInOut,
      transitionDuration: const Duration(milliseconds: 300),
    );
  }
  
  // 底部滑出动画
  static GetPageRoute bottomSlideTransition(
    Widget page, {
    RouteSettings? settings,
    bool popGesture = true,
  }) {
    return GetPageRoute(
      page: () => page,
      settings: settings,
      popGesture: popGesture,
      transition: Transition.downToUp,
      curve: Curves.easeInOut,
      transitionDuration: const Duration(milliseconds: 300),
    );
  }
  
  // 自定义动画
  static GetPageRoute customTransition(
    Widget page, {
    RouteSettings? settings,
    bool popGesture = true,
    Curve curve = Curves.easeInOut,
    Duration duration = const Duration(milliseconds: 300),
    Widget Function(BuildContext, Animation<double>, Animation<double>, Widget)?
        customTransition,
  }) {
    return GetPageRoute(
      page: () => page,
      settings: settings,
      popGesture: popGesture,
      customTransition: customTransition,
      curve: curve,
      transitionDuration: duration,
    );
  }
  
  // 根据路由类型选择动画
  static GetPageRoute getTransition(
    Widget page, {
    RouteSettings? settings,
    bool popGesture = true,
    TransitionType type = TransitionType.defaultTransition,
  }) {
    switch (type) {
      case TransitionType.fade:
        return fadeTransition(page, settings: settings, popGesture: popGesture);
      case TransitionType.scale:
        return scaleTransition(page, settings: settings, popGesture: popGesture);
      case TransitionType.bottomSlide:
        return bottomSlideTransition(
          page,
          settings: settings,
          popGesture: popGesture,
        );
      case TransitionType.defaultTransition:
      default:
        return defaultTransition(page, settings: settings, popGesture: popGesture);
    }
  }
}

enum TransitionType {
  defaultTransition,
  fade,
  scale,
  bottomSlide,
} 