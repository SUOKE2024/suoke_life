import 'package:flutter/material.dart';

/// 网格组件
class AppGrid extends StatelessWidget {
  final List<Widget> children;
  final int crossAxisCount;
  final double mainAxisSpacing;
  final double crossAxisSpacing;
  final double childAspectRatio;
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
  final int? semanticChildCount;
  final String? restorationId;
  final Clip clipBehavior;
  
  const AppGrid({
    super.key,
    required this.children,
    this.crossAxisCount = 2,
    this.mainAxisSpacing = 8,
    this.crossAxisSpacing = 8,
    this.childAspectRatio = 1,
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
    this.semanticChildCount,
    this.restorationId,
    this.clipBehavior = Clip.hardEdge,
  });

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      crossAxisCount: crossAxisCount,
      mainAxisSpacing: mainAxisSpacing,
      crossAxisSpacing: crossAxisSpacing,
      childAspectRatio: childAspectRatio,
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
      semanticChildCount: semanticChildCount,
      restorationId: restorationId,
      clipBehavior: clipBehavior,
      children: children,
    );
  }
}

/// 自适应网格组件
class AppGridExtent extends StatelessWidget {
  final List<Widget> children;
  final double maxCrossAxisExtent;
  final double mainAxisSpacing;
  final double crossAxisSpacing;
  final double childAspectRatio;
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
  final int? semanticChildCount;
  final String? restorationId;
  final Clip clipBehavior;
  
  const AppGridExtent({
    super.key,
    required this.children,
    this.maxCrossAxisExtent = 200,
    this.mainAxisSpacing = 8,
    this.crossAxisSpacing = 8,
    this.childAspectRatio = 1,
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
    this.semanticChildCount,
    this.restorationId,
    this.clipBehavior = Clip.hardEdge,
  });

  @override
  Widget build(BuildContext context) {
    return GridView.extent(
      maxCrossAxisExtent: maxCrossAxisExtent,
      mainAxisSpacing: mainAxisSpacing,
      crossAxisSpacing: crossAxisSpacing,
      childAspectRatio: childAspectRatio,
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
      semanticChildCount: semanticChildCount,
      restorationId: restorationId,
      clipBehavior: clipBehavior,
      children: children,
    );
  }
} 