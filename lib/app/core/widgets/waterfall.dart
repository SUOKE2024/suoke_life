/// 瀑布流组件
class Waterfall extends StatelessWidget {
  final List<Widget> children;
  final int crossAxisCount;
  final double spacing;
  final double runSpacing;
  final EdgeInsets? padding;
  final ScrollController? controller;
  final bool primary;
  final bool shrinkWrap;
  final ScrollPhysics? physics;
  final bool addAutomaticKeepAlives;
  final bool addRepaintBoundaries;
  final bool addSemanticIndexes;
  final double? cacheExtent;
  final int? semanticChildCount;
  final DragStartBehavior dragStartBehavior;
  final ScrollViewKeyboardDismissBehavior keyboardDismissBehavior;
  final String? restorationId;
  final Clip clipBehavior;

  const Waterfall({
    super.key,
    required this.children,
    this.crossAxisCount = 2,
    this.spacing = 8,
    this.runSpacing = 8,
    this.padding,
    this.controller,
    this.primary = false,
    this.shrinkWrap = false,
    this.physics,
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
    return CustomScrollView(
      controller: controller,
      primary: primary,
      physics: physics,
      shrinkWrap: shrinkWrap,
      cacheExtent: cacheExtent,
      semanticChildCount: semanticChildCount,
      dragStartBehavior: dragStartBehavior,
      keyboardDismissBehavior: keyboardDismissBehavior,
      restorationId: restorationId,
      clipBehavior: clipBehavior,
      slivers: [
        SliverPadding(
          padding: padding ?? EdgeInsets.zero,
          sliver: SliverGrid(
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: crossAxisCount,
              mainAxisSpacing: runSpacing,
              crossAxisSpacing: spacing,
              childAspectRatio: 1,
            ),
            delegate: SliverChildBuilderDelegate(
              (context, index) => children[index],
              childCount: children.length,
              addAutomaticKeepAlives: addAutomaticKeepAlives,
              addRepaintBoundaries: addRepaintBoundaries,
              addSemanticIndexes: addSemanticIndexes,
            ),
          ),
        ),
      ],
    );
  }
} 