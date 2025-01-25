import 'package:flutter/material.dart';

/// 标签组件
class AppTag extends StatelessWidget {
  final String text;
  final Color? backgroundColor;
  final Color? textColor;
  final double? fontSize;
  final EdgeInsets? padding;
  final double? borderRadius;
  final VoidCallback? onTap;
  final bool outlined;
  final Color? borderColor;
  final double? borderWidth;
  final Widget? icon;
  final bool closable;
  final VoidCallback? onClose;

  const AppTag({
    super.key,
    required this.text,
    this.color,
    this.backgroundColor,
    this.textStyle,
    this.fontSize,
    this.padding,
    this.borderRadius,
    this.onTap,
    this.icon,
    this.outlined = false,
    this.closable = false,
    this.onClose,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultColor = color ?? theme.primaryColor;
    final defaultBackgroundColor = backgroundColor ?? defaultColor.withOpacity(0.1);

    Widget child = Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (icon != null) ...[
          icon!,
          const SizedBox(width: 4),
        ],
        Text(
          text,
          style: textStyle?.copyWith(
            fontSize: fontSize,
            color: outlined ? defaultColor : color,
          ) ??
              TextStyle(
                fontSize: fontSize ?? 12,
                color: outlined ? defaultColor : color,
              ),
        ),
        if (closable) ...[
          const SizedBox(width: 4),
          InkWell(
            onTap: onClose,
            child: Icon(
              Icons.close,
              size: (fontSize ?? 12) + 2,
              color: outlined ? defaultColor : color,
            ),
          ),
        ],
      ],
    );

    if (onTap != null) {
      child = InkWell(
        onTap: onTap,
        borderRadius: borderRadius ?? BorderRadius.circular(4),
        child: child,
      );
    }

    return Container(
      padding: padding ?? const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: outlined ? Colors.transparent : defaultBackgroundColor,
        border: outlined ? Border.all(color: defaultColor) : null,
        borderRadius: borderRadius ?? BorderRadius.circular(4),
      ),
      child: child,
    );
  }
} 