import 'package:flutter/material.dart';

/// 标签页组件
class AppTabs extends StatelessWidget {
  final List<AppTab> tabs;
  final int currentIndex;
  final ValueChanged<int>? onChanged;
  final bool isScrollable;
  final Color? backgroundColor;
  final Color? indicatorColor;
  final Color? selectedLabelColor;
  final Color? unselectedLabelColor;
  final TextStyle? labelStyle;
  final TextStyle? unselectedLabelStyle;
  final EdgeInsets? padding;
  final double? indicatorWeight;
  final TabBarIndicatorSize? indicatorSize;
  final BorderRadius? indicatorBorderRadius;
  
  const AppTabs({
    super.key,
    required this.tabs,
    required this.currentIndex,
    this.onChanged,
    this.isScrollable = false,
    this.backgroundColor,
    this.indicatorColor,
    this.selectedLabelColor,
    this.unselectedLabelColor,
    this.labelStyle,
    this.unselectedLabelStyle,
    this.padding,
    this.indicatorWeight,
    this.indicatorSize,
    this.indicatorBorderRadius,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Container(
      color: backgroundColor,
      child: TabBar(
        tabs: tabs.map((tab) {
          return Tab(
            icon: tab.icon,
            iconMargin: tab.iconMargin ?? const EdgeInsets.only(bottom: 8),
            text: tab.text,
            child: tab.child,
          );
        }).toList(),
        controller: TabController(
          length: tabs.length,
          vsync: Scaffold.of(context),
          initialIndex: currentIndex,
        )..addListener(() {
          if (onChanged != null) {
            onChanged!(currentIndex);
          }
        }),
        isScrollable: isScrollable,
        indicatorColor: indicatorColor ?? theme.primaryColor,
        labelColor: selectedLabelColor ?? theme.primaryColor,
        unselectedLabelColor: unselectedLabelColor ?? theme.unselectedWidgetColor,
        labelStyle: labelStyle,
        unselectedLabelStyle: unselectedLabelStyle,
        padding: padding,
        indicatorWeight: indicatorWeight ?? 2,
        indicatorSize: indicatorSize ?? TabBarIndicatorSize.tab,
        indicator: indicatorBorderRadius != null
            ? BoxDecoration(
                borderRadius: indicatorBorderRadius,
                color: indicatorColor ?? theme.primaryColor,
              )
            : null,
      ),
    );
  }
}

/// 标签页内容组件
class AppTabView extends StatelessWidget {
  final List<Widget> children;
  final int currentIndex;
  final ValueChanged<int>? onChanged;
  final ScrollPhysics? physics;
  final DragStartBehavior dragStartBehavior;
  
  const AppTabView({
    super.key,
    required this.children,
    required this.currentIndex,
    this.onChanged,
    this.physics,
    this.dragStartBehavior = DragStartBehavior.start,
  });

  @override
  Widget build(BuildContext context) {
    return TabBarView(
      controller: TabController(
        length: children.length,
        vsync: Scaffold.of(context),
        initialIndex: currentIndex,
      )..addListener(() {
        if (onChanged != null) {
          onChanged!(currentIndex);
        }
      }),
      physics: physics,
      dragStartBehavior: dragStartBehavior,
      children: children,
    );
  }
}

/// 标签页项
class AppTab {
  final String? text;
  final Widget? icon;
  final Widget? child;
  final EdgeInsets? iconMargin;
  
  const AppTab({
    this.text,
    this.icon,
    this.child,
    this.iconMargin,
  }) : assert(text != null || icon != null || child != null);
} 