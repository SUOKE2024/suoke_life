import 'package:flutter/material.dart';

/// 列表组件
class AppListView extends StatelessWidget {
  final List<Widget> children;
  final ScrollController? controller;
  final bool shrinkWrap;
  final ScrollPhysics? physics;
  final EdgeInsets? padding;
  final bool primary;
  final bool reverse;
  final double? itemExtent;
  final bool addAutomaticKeepAlives;
  final bool addRepaintBoundaries;
  final bool addSemanticIndexes;
  final double? cacheExtent;
  final int? semanticChildCount;
  final DragStartBehavior dragStartBehavior;
  final ScrollViewKeyboardDismissBehavior keyboardDismissBehavior;
  final String? restorationId;
  final Clip clipBehavior;
  
  const AppListView({
    super.key,
    required this.children,
    this.controller,
    this.shrinkWrap = false,
    this.physics,
    this.padding,
    this.primary,
    this.reverse = false,
    this.itemExtent,
    this.addAutomaticKeepAlives = true,
    this.addRepaintBoundaries = true,
    this.addSemanticIndexes = true,
    this.cacheExtent,
    this.semanticChildCount,
    this.dragStartBehavior = DragStartBehavior.start,
    this.keyboardDismissBehavior = ScrollViewKeyboardDismissBehavior.manual,
    this.restorationId,
    this.clipBehavior = Clip.hardEdge,
  });

  @override
  Widget build(BuildContext context) {
    return ListView(
      controller: controller,
      shrinkWrap: shrinkWrap,
      physics: physics,
      padding: padding,
      primary: primary,
      reverse: reverse,
      itemExtent: itemExtent,
      addAutomaticKeepAlives: addAutomaticKeepAlives,
      addRepaintBoundaries: addRepaintBoundaries,
      addSemanticIndexes: addSemanticIndexes,
      cacheExtent: cacheExtent,
      semanticChildCount: semanticChildCount,
      dragStartBehavior: dragStartBehavior,
      keyboardDismissBehavior: keyboardDismissBehavior,
      restorationId: restorationId,
      clipBehavior: clipBehavior,
      children: children,
    );
  }
}

/// 分隔列表组件
class AppListViewSeparated extends StatelessWidget {
  final List<Widget> children;
  final Widget separator;
  final ScrollController? controller;
  final bool shrinkWrap;
  final ScrollPhysics? physics;
  final EdgeInsets? padding;
  final bool primary;
  final bool reverse;
  final bool addAutomaticKeepAlives;
  final bool addRepaintBoundaries;
  final bool addSemanticIndexes;
  final double? cacheExtent;
  final DragStartBehavior dragStartBehavior;
  final ScrollViewKeyboardDismissBehavior keyboardDismissBehavior;
  final String? restorationId;
  final Clip clipBehavior;
  
  const AppListViewSeparated({
    super.key,
    required this.children,
    required this.separator,
    this.controller,
    this.shrinkWrap = false,
    this.physics,
    this.padding,
    this.primary,
    this.reverse = false,
    this.addAutomaticKeepAlives = true,
    this.addRepaintBoundaries = true,
    this.addSemanticIndexes = true,
    this.cacheExtent,
    this.dragStartBehavior = DragStartBehavior.start,
    this.keyboardDismissBehavior = ScrollViewKeyboardDismissBehavior.manual,
    this.restorationId,
    this.clipBehavior = Clip.hardEdge,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      itemCount: children.length,
      separatorBuilder: (_, __) => separator,
      itemBuilder: (_, index) => children[index],
      controller: controller,
      shrinkWrap: shrinkWrap,
      physics: physics,
      padding: padding,
      primary: primary,
      reverse: reverse,
      addAutomaticKeepAlives: addAutomaticKeepAlives,
      addRepaintBoundaries: addRepaintBoundaries,
      addSemanticIndexes: addSemanticIndexes,
      cacheExtent: cacheExtent,
      dragStartBehavior: dragStartBehavior,
      keyboardDismissBehavior: keyboardDismissBehavior,
      restorationId: restorationId,
      clipBehavior: clipBehavior,
    );
  }
} 