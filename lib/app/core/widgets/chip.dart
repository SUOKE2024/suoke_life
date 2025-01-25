import 'package:flutter/material.dart';

/// 标签组件
class AppChip extends StatelessWidget {
  final String label;
  final Widget? avatar;
  final Widget? deleteIcon;
  final VoidCallback? onDeleted;
  final Color? backgroundColor;
  final Color? labelColor;
  final TextStyle? labelStyle;
  final EdgeInsets? padding;
  final double? borderRadius;
  final VoidCallback? onTap;
  final bool selected;
  final Color? selectedColor;
  final bool disabled;
  
  const AppChip({
    super.key,
    required this.label,
    this.avatar,
    this.deleteIcon,
    this.onDeleted,
    this.backgroundColor,
    this.labelColor,
    this.labelStyle,
    this.padding,
    this.borderRadius,
    this.onTap,
    this.selected = false,
    this.selectedColor,
    this.disabled = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultBackgroundColor = backgroundColor ?? theme.chipTheme.backgroundColor;
    final defaultSelectedColor = selectedColor ?? theme.primaryColor;
    
    Widget chip = Chip(
      label: Text(label),
      avatar: avatar,
      deleteIcon: deleteIcon,
      onDeleted: disabled ? null : onDeleted,
      backgroundColor: selected ? defaultSelectedColor : defaultBackgroundColor,
      labelStyle: labelStyle?.copyWith(
        color: labelColor,
      ) ?? TextStyle(
        color: labelColor ?? (selected ? Colors.white : null),
      ),
      padding: padding,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(borderRadius ?? 20),
      ),
    );

    if (onTap != null && !disabled) {
      chip = InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(borderRadius ?? 20),
        child: chip,
      );
    }

    return chip;
  }
} 