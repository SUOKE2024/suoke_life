/// 徽章组件
class AppBadge extends StatelessWidget {
  final Widget? child;
  final String? text;
  final Color? color;
  final Color? textColor;
  final double? size;
  final EdgeInsets? padding;
  final BorderRadius? borderRadius;
  final bool dot;
  final bool showZero;
  final int? count;
  final int? maxCount;
  final TextStyle? textStyle;
  final AlignmentGeometry alignment;
  final bool visible;

  const AppBadge({
    super.key,
    this.child,
    this.text,
    this.color,
    this.textColor,
    this.size,
    this.padding,
    this.borderRadius,
    this.dot = false,
    this.showZero = false,
    this.count,
    this.maxCount = 99,
    this.textStyle,
    this.alignment = const Alignment(1, -1),
    this.visible = true,
  });

  @override
  Widget build(BuildContext context) {
    if (!visible) return child ?? const SizedBox();

    final theme = Theme.of(context);
    final defaultColor = color ?? theme.colorScheme.error;
    final defaultTextColor = textColor ?? Colors.white;
    final defaultSize = size ?? (dot ? 8.0 : 16.0);

    Widget badge;
    if (dot) {
      badge = Container(
        width: defaultSize,
        height: defaultSize,
        decoration: BoxDecoration(
          color: defaultColor,
          shape: BoxShape.circle,
        ),
      );
    } else if (text != null || count != null) {
      final showText = text ?? _formatCount(count!, maxCount!);
      if (!showZero && showText == '0') {
        return child ?? const SizedBox();
      }

      badge = Container(
        padding: padding ??
            EdgeInsets.symmetric(
              horizontal: showText.length == 1 ? 4 : 6,
              vertical: 2,
            ),
        decoration: BoxDecoration(
          color: defaultColor,
          borderRadius: borderRadius ?? BorderRadius.circular(defaultSize / 2),
        ),
        child: Text(
          showText,
          style: textStyle?.copyWith(color: defaultTextColor) ??
              TextStyle(
                color: defaultTextColor,
                fontSize: defaultSize * 0.75,
                fontWeight: FontWeight.bold,
              ),
        ),
      );
    } else {
      return child ?? const SizedBox();
    }

    if (child == null) return badge;

    return Stack(
      clipBehavior: Clip.none,
      children: [
        child!,
        Positioned.fill(
          child: Align(
            alignment: alignment,
            child: Transform.translate(
              offset: Offset(defaultSize / 2, -defaultSize / 2),
              child: badge,
            ),
          ),
        ),
      ],
    );
  }

  String _formatCount(int count, int maxCount) {
    if (count <= maxCount) return count.toString();
    return '$maxCount+';
  }
} 