import 'package:flutter/material.dart';

/// 下拉刷新组件
class AppRefresh extends StatelessWidget {
  final Widget child;
  final Future<void> Function() onRefresh;
  final bool enablePullUp;
  final Future<void> Function()? onLoadMore;
  final ScrollController? controller;
  final Color? indicatorColor;
  final double? indicatorStrokeWidth;
  final double? displacement;
  final bool showScrollbar;
  final ScrollPhysics? physics;
  final EdgeInsets? padding;
  
  const AppRefresh({
    super.key,
    required this.child,
    required this.onRefresh,
    this.enablePullUp = false,
    this.onLoadMore,
    this.controller,
    this.indicatorColor,
    this.indicatorStrokeWidth,
    this.displacement,
    this.showScrollbar = true,
    this.physics,
    this.padding,
  }) : assert(!enablePullUp || onLoadMore != null);

  @override
  Widget build(BuildContext context) {
    Widget content = RefreshIndicator(
      onRefresh: onRefresh,
      color: indicatorColor,
      strokeWidth: indicatorStrokeWidth ?? 2.0,
      displacement: displacement ?? 40.0,
      child: NotificationListener<ScrollNotification>(
        onNotification: (notification) {
          // 处理上拉加载更多
          if (enablePullUp && 
              notification is ScrollEndNotification &&
              notification.metrics.extentAfter == 0) {
            onLoadMore?.call();
          }
          return false;
        },
        child: SingleChildScrollView(
          controller: controller,
          physics: physics ?? const AlwaysScrollableScrollPhysics(),
          padding: padding,
          child: child,
        ),
      ),
    );

    if (showScrollbar) {
      content = Scrollbar(
        controller: controller,
        child: content,
      );
    }

    return content;
  }
}

/// 刷新状态包装组件
class AppRefreshWrapper extends StatefulWidget {
  final Widget child;
  final Future<void> Function() onRefresh;
  final bool enablePullUp;
  final Future<void> Function()? onLoadMore;
  final bool initialRefresh;
  
  const AppRefreshWrapper({
    super.key,
    required this.child,
    required this.onRefresh,
    this.enablePullUp = false,
    this.onLoadMore,
    this.initialRefresh = true,
  });

  @override
  State<AppRefreshWrapper> createState() => _AppRefreshWrapperState();
}

class _AppRefreshWrapperState extends State<AppRefreshWrapper> {
  @override
  void initState() {
    super.initState();
    if (widget.initialRefresh) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        widget.onRefresh();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppRefresh(
      onRefresh: widget.onRefresh,
      enablePullUp: widget.enablePullUp,
      onLoadMore: widget.onLoadMore,
      child: widget.child,
    );
  }
} 