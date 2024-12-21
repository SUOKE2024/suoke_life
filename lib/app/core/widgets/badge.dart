import 'package:flutter/material.dart';

/// 徽标组件
class AppBadge extends StatelessWidget {
  final Widget child;
  final String? text;
  final Widget? content;
  final Color? backgroundColor;
  final Color? textColor;
  final TextStyle? textStyle;
  final double? size;
  final EdgeInsets? padding;
  final BorderRadius? borderRadius;
  final Alignment alignment;
  final bool dot;
  final bool hidden;
  
  const AppBadge({
    super.key,
    required this.child,
    this.text,
    this.content,
    this.backgroundColor,
    this.textColor,
    this.textStyle,
    this.size,
    this.padding,
    this.borderRadius,
    this.alignment = Alignment.topRight,
    this.dot = false,
    this.hidden = false,
  }) : assert(dot || text != null || content != null);

  @override
  Widget build(BuildContext context) {
    if (hidden) {
      return child;
    }

    final theme = Theme.of(context);
    final defaultBackgroundColor = backgroundColor ?? theme.colorScheme.error;
    final defaultTextColor = textColor ?? Colors.white;
    final defaultSize = size ?? (dot ? 8 : 16);

    Widget badge = Container(
      width: dot ? defaultSize : null,
      height: dot ? defaultSize : null,
      padding: dot ? null : (padding ?? const EdgeInsets.symmetric(
        horizontal: 6,
        vertical: 2,
      )),
      decoration: BoxDecoration(
        color: defaultBackgroundColor,
        borderRadius: borderRadius ?? BorderRadius.circular(defaultSize / 2),
      ),
      child: dot ? null : Center(
        child: content ?? Text(
          text!,
          style: textStyle?.copyWith(
            color: defaultTextColor,
          ) ?? TextStyle(
            color: defaultTextColor,
            fontSize: 12,
          ),
        ),
      ),
    );

    return Stack(
      clipBehavior: Clip.none,
      children: [
        child,
        Positioned.fill(
          child: Align(
            alignment: alignment,
            child: badge,
          ),
        ),
      ],
    );
  }
} 