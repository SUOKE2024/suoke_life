/// 标签页组件
class AppTabs extends StatelessWidget {
  final List<TabItem> tabs;
  final int? currentIndex;
  final ValueChanged<int>? onChanged;
  final bool isScrollable;
  final Color? indicatorColor;
  final Color? labelColor;
  final Color? unselectedLabelColor;
  final TextStyle? labelStyle;
  final TextStyle? unselectedLabelStyle;
  final EdgeInsets? padding;
  final double? indicatorWeight;
  final TabBarIndicatorSize? indicatorSize;
  final bool showDivider;
  final Widget? divider;

  const AppTabs({
    super.key,
    required this.tabs,
    this.currentIndex,
    this.onChanged,
    this.isScrollable = false,
    this.indicatorColor,
    this.labelColor,
    this.unselectedLabelColor,
    this.labelStyle,
    this.unselectedLabelStyle,
    this.padding,
    this.indicatorWeight,
    this.indicatorSize,
    this.showDivider = true,
    this.divider,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        TabBar(
          tabs: tabs.map((tab) {
            return Tab(
              icon: tab.icon,
              iconMargin: tab.iconMargin ?? const EdgeInsets.only(bottom: 4),
              text: tab.text,
              child: tab.child,
            );
          }).toList(),
          controller: TabController(
            length: tabs.length,
            vsync: Scaffold.of(context),
            initialIndex: currentIndex ?? 0,
          ),
          onTap: onChanged,
          isScrollable: isScrollable,
          indicatorColor: indicatorColor ?? theme.primaryColor,
          labelColor: labelColor ?? theme.primaryColor,
          unselectedLabelColor: unselectedLabelColor ?? theme.unselectedWidgetColor,
          labelStyle: labelStyle,
          unselectedLabelStyle: unselectedLabelStyle,
          padding: padding,
          indicatorWeight: indicatorWeight ?? 2.0,
          indicatorSize: indicatorSize ?? TabBarIndicatorSize.tab,
        ),
        if (showDivider) divider ?? const Divider(height: 1),
      ],
    );
  }
}

/// 标签页项
class TabItem {
  final String? text;
  final Widget? icon;
  final EdgeInsetsGeometry? iconMargin;
  final Widget? child;

  const TabItem({
    this.text,
    this.icon,
    this.iconMargin,
    this.child,
  }) : assert(text != null || icon != null || child != null);
} 