import 'package:flutter/material.dart';

/// 底部导航栏组件
class AppBottomBar extends StatelessWidget {
  final List<AppBottomBarItem> items;
  final int currentIndex;
  final ValueChanged<int>? onTap;
  final Color? backgroundColor;
  final Color? selectedItemColor;
  final Color? unselectedItemColor;
  final double? elevation;
  final double? iconSize;
  final TextStyle? selectedLabelStyle;
  final TextStyle? unselectedLabelStyle;
  final bool showLabel;
  
  const AppBottomBar({
    super.key,
    required this.items,
    required this.currentIndex,
    this.onTap,
    this.backgroundColor,
    this.selectedItemColor,
    this.unselectedItemColor,
    this.elevation,
    this.iconSize,
    this.selectedLabelStyle,
    this.unselectedLabelStyle,
    this.showLabel = true,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return BottomNavigationBar(
      items: items.map((item) {
        return BottomNavigationBarItem(
          icon: item.icon,
          activeIcon: item.activeIcon ?? item.icon,
          label: showLabel ? item.label : null,
          backgroundColor: item.backgroundColor,
          tooltip: item.tooltip,
        );
      }).toList(),
      currentIndex: currentIndex,
      onTap: onTap,
      backgroundColor: backgroundColor,
      selectedItemColor: selectedItemColor ?? theme.primaryColor,
      unselectedItemColor: unselectedItemColor ?? theme.unselectedWidgetColor,
      elevation: elevation,
      iconSize: iconSize ?? 24,
      selectedLabelStyle: selectedLabelStyle,
      unselectedLabelStyle: unselectedLabelStyle,
      type: BottomNavigationBarType.fixed,
      showSelectedLabels: showLabel,
      showUnselectedLabels: showLabel,
    );
  }
}

/// 底部导航项
class AppBottomBarItem {
  final String label;
  final Widget icon;
  final Widget? activeIcon;
  final Color? backgroundColor;
  final String? tooltip;
  
  const AppBottomBarItem({
    required this.label,
    required this.icon,
    this.activeIcon,
    this.backgroundColor,
    this.tooltip,
  });
} 