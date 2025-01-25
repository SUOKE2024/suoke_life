import 'package:flutter/material.dart';

/// 进度条组件
class AppProgress extends StatelessWidget {
  final double? value;
  final Color? backgroundColor;
  final Color? valueColor;
  final double height;
  final BorderRadius? borderRadius;
  final String? label;
  final TextStyle? labelStyle;
  final EdgeInsets? padding;
  final bool showPercentage;
  
  const AppProgress({
    super.key,
    this.value,
    this.backgroundColor,
    this.valueColor,
    this.height = 4,
    this.borderRadius,
    this.label,
    this.labelStyle,
    this.padding,
    this.showPercentage = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultBackgroundColor = backgroundColor ?? theme.dividerColor;
    final defaultValueColor = valueColor ?? theme.primaryColor;
    final defaultBorderRadius = borderRadius ?? BorderRadius.circular(height / 2);
    final percentage = value != null ? (value! * 100).toInt() : null;
    final displayLabel = label ?? (showPercentage && percentage != null ? '$percentage%' : null);

    return Padding(
      padding: padding ?? EdgeInsets.zero,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          if (displayLabel != null) ...[
            Text(
              displayLabel,
              style: labelStyle ?? theme.textTheme.bodySmall,
            ),
            const SizedBox(height: 8),
          ],
          ClipRRect(
            borderRadius: defaultBorderRadius,
            child: SizedBox(
              height: height,
              child: LinearProgressIndicator(
                value: value,
                backgroundColor: defaultBackgroundColor,
                valueColor: AlwaysStoppedAnimation(defaultValueColor),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// 环形进度条组件
class AppCircularProgress extends StatelessWidget {
  final double? value;
  final Color? backgroundColor;
  final Color? valueColor;
  final double size;
  final double strokeWidth;
  final String? label;
  final TextStyle? labelStyle;
  final EdgeInsets? padding;
  final bool showPercentage;
  
  const AppCircularProgress({
    super.key,
    this.value,
    this.backgroundColor,
    this.valueColor,
    this.size = 36,
    this.strokeWidth = 4,
    this.label,
    this.labelStyle,
    this.padding,
    this.showPercentage = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultBackgroundColor = backgroundColor ?? theme.dividerColor;
    final defaultValueColor = valueColor ?? theme.primaryColor;
    final percentage = value != null ? (value! * 100).toInt() : null;
    final displayLabel = label ?? (showPercentage && percentage != null ? '$percentage%' : null);

    return Padding(
      padding: padding ?? EdgeInsets.zero,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: size,
            height: size,
            child: CircularProgressIndicator(
              value: value,
              backgroundColor: defaultBackgroundColor,
              valueColor: AlwaysStoppedAnimation(defaultValueColor),
              strokeWidth: strokeWidth,
            ),
          ),
          if (displayLabel != null) ...[
            const SizedBox(height: 8),
            Text(
              displayLabel,
              style: labelStyle ?? theme.textTheme.bodySmall,
            ),
          ],
        ],
      ),
    );
  }
} 