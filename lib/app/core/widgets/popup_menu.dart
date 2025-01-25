import 'package:flutter/material.dart';

/// 弹出菜单组件
class AppPopupMenu<T> extends StatelessWidget {
  final Widget child;
  final List<AppPopupMenuItem<T>> items;
  final T? initialValue;
  final ValueChanged<T>? onSelected;
  final VoidCallback? onCanceled;
  final EdgeInsets? padding;
  final Color? color;
  final double? elevation;
  final BorderRadius? borderRadius;
  final Offset? offset;
  final bool enabled;
  
  const AppPopupMenu({
    super.key,
    required this.child,
    required this.items,
    this.initialValue,
    this.onSelected,
    this.onCanceled,
    this.padding,
    this.color,
    this.elevation,
    this.borderRadius,
    this.offset,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<T>(
      itemBuilder: (context) => items.map((item) {
        if (item.isDivider) {
          return const PopupMenuDivider();
        }
        return PopupMenuItem<T>(
          value: item.value,
          enabled: item.enabled,
          padding: item.padding,
          height: item.height,
          child: Row(
            children: [
              if (item.icon != null) ...[
                item.icon!,
                const SizedBox(width: 8),
              ],
              Expanded(child: Text(item.text)),
              if (item.trailing != null)
                item.trailing!,
            ],
          ),
        );
      }).toList(),
      initialValue: initialValue,
      onSelected: onSelected,
      onCanceled: onCanceled,
      padding: padding ?? EdgeInsets.zero,
      color: color,
      elevation: elevation,
      shape: RoundedRectangleBorder(
        borderRadius: borderRadius ?? BorderRadius.circular(4),
      ),
      offset: offset ?? Offset.zero,
      enabled: enabled,
      child: child,
    );
  }

  /// 显示弹出菜单
  static Future<T?> show<T>({
    required BuildContext context,
    required List<AppPopupMenuItem<T>> items,
    required RelativeRect position,
    T? initialValue,
    ValueChanged<T>? onSelected,
    VoidCallback? onCanceled,
    EdgeInsets? padding,
    Color? color,
    double? elevation,
    BorderRadius? borderRadius,
  }) {
    return showMenu<T>(
      context: context,
      items: items.map((item) {
        if (item.isDivider) {
          return const PopupMenuDivider();
        }
        return PopupMenuItem<T>(
          value: item.value,
          enabled: item.enabled,
          padding: item.padding,
          height: item.height,
          child: Row(
            children: [
              if (item.icon != null) ...[
                item.icon!,
                const SizedBox(width: 8),
              ],
              Expanded(child: Text(item.text)),
              if (item.trailing != null)
                item.trailing!,
            ],
          ),
        );
      }).toList(),
      initialValue: initialValue,
      position: position,
      color: color,
      elevation: elevation,
      shape: RoundedRectangleBorder(
        borderRadius: borderRadius ?? BorderRadius.circular(4),
      ),
    );
  }
}

/// 弹出菜单项
class AppPopupMenuItem<T> {
  final T? value;
  final String text;
  final Widget? icon;
  final Widget? trailing;
  final bool enabled;
  final bool isDivider;
  final EdgeInsets? padding;
  final double? height;
  
  const AppPopupMenuItem({
    this.value,
    required this.text,
    this.icon,
    this.trailing,
    this.enabled = true,
    this.isDivider = false,
    this.padding,
    this.height,
  });

  /// 创建分割线
  const AppPopupMenuItem.divider()
      : value = null,
        text = '',
        icon = null,
        trailing = null,
        enabled = false,
        isDivider = true,
        padding = null,
        height = null;
} 