import 'package:flutter/material.dart';

/// 抽屉组件
class AppDrawer extends StatelessWidget {
  final Widget? header;
  final List<AppDrawerItem> items;
  final int? selectedIndex;
  final ValueChanged<int>? onChanged;
  final Widget? footer;
  final Color? backgroundColor;
  final double? width;
  final EdgeInsets? padding;
  
  const AppDrawer({
    super.key,
    this.header,
    required this.items,
    this.selectedIndex,
    this.onChanged,
    this.footer,
    this.backgroundColor,
    this.width,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Drawer(
      backgroundColor: backgroundColor,
      width: width,
      child: SafeArea(
        child: Padding(
          padding: padding ?? EdgeInsets.zero,
          child: Column(
            children: [
              if (header != null) header!,
              Expanded(
                child: ListView.builder(
                  itemCount: items.length,
                  itemBuilder: (context, index) {
                    final item = items[index];
                    final selected = selectedIndex == index;
                    
                    if (item.isDivider) {
                      return const Divider();
                    }

                    return ListTile(
                      leading: item.icon,
                      title: Text(item.title),
                      subtitle: item.subtitle != null
                          ? Text(item.subtitle!)
                          : null,
                      trailing: item.trailing,
                      selected: selected,
                      enabled: item.enabled,
                      onTap: item.enabled
                          ? () => onChanged?.call(index)
                          : null,
                    );
                  },
                ),
              ),
              if (footer != null) footer!,
            ],
          ),
        ),
      ),
    );
  }
}

/// 抽屉项
class AppDrawerItem {
  final String title;
  final String? subtitle;
  final Widget? icon;
  final Widget? trailing;
  final bool enabled;
  final bool isDivider;
  
  const AppDrawerItem({
    required this.title,
    this.subtitle,
    this.icon,
    this.trailing,
    this.enabled = true,
    this.isDivider = false,
  });

  /// 创建分割线
  const AppDrawerItem.divider()
      : title = '',
        subtitle = null,
        icon = null,
        trailing = null,
        enabled = false,
        isDivider = true;
} 