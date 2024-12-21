import 'package:flutter/material.dart';

/// 图标组件
class AppIcon extends StatelessWidget {
  final IconData icon;
  final double? size;
  final Color? color;
  final String? tooltip;
  final VoidCallback? onTap;
  final EdgeInsets? padding;
  final BorderRadius? borderRadius;
  final Color? backgroundColor;
  
  const AppIcon({
    super.key,
    required this.icon,
    this.size,
    this.color,
    this.tooltip,
    this.onTap,
    this.padding,
    this.borderRadius,
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    Widget iconWidget = Icon(
      icon,
      size: size,
      color: color,
    );

    if (tooltip != null) {
      iconWidget = Tooltip(
        message: tooltip!,
        child: iconWidget,
      );
    }

    if (backgroundColor != null) {
      iconWidget = Container(
        padding: padding ?? const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: borderRadius ?? BorderRadius.circular(4),
        ),
        child: iconWidget,
      );
    } else if (padding != null) {
      iconWidget = Padding(
        padding: padding!,
        child: iconWidget,
      );
    }

    if (onTap != null) {
      iconWidget = InkWell(
        onTap: onTap,
        borderRadius: borderRadius,
        child: iconWidget,
      );
    }

    return iconWidget;
  }
} 