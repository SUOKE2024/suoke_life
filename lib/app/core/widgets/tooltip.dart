/// 提示组件
class AppTooltip extends StatelessWidget {
  final Widget child;
  final String message;
  final Color? color;
  final Color? textColor;
  final TextStyle? textStyle;
  final EdgeInsets? padding;
  final double? fontSize;
  final BorderRadius? borderRadius;
  final Duration? showDuration;
  final bool preferBelow;
  final bool enableFeedback;
  final bool? excludeFromSemantics;
  final TooltipTriggerMode? triggerMode;
  final bool? allowHover;

  const AppTooltip({
    super.key,
    required this.child,
    required this.message,
    this.color,
    this.textColor,
    this.textStyle,
    this.padding,
    this.fontSize,
    this.borderRadius,
    this.showDuration,
    this.preferBelow = true,
    this.enableFeedback = true,
    this.excludeFromSemantics,
    this.triggerMode,
    this.allowHover,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultColor = color ?? theme.colorScheme.secondary;
    final defaultTextColor = textColor ?? Colors.white;

    return Tooltip(
      message: message,
      textStyle: textStyle?.copyWith(color: defaultTextColor) ??
          TextStyle(
            color: defaultTextColor,
            fontSize: fontSize ?? 14,
          ),
      decoration: ShapeDecoration(
        color: defaultColor,
        shape: RoundedRectangleBorder(
          borderRadius: borderRadius ?? BorderRadius.circular(4),
        ),
      ),
      padding: padding ?? const EdgeInsets.symmetric(
        horizontal: 16,
        vertical: 8,
      ),
      showDuration: showDuration ?? const Duration(seconds: 2),
      preferBelow: preferBelow,
      enableFeedback: enableFeedback,
      excludeFromSemantics: excludeFromSemantics,
      triggerMode: triggerMode,
      child: child,
    );
  }

  /// 显示提示
  static void show(
    BuildContext context,
    String message, {
    Color? color,
    Color? textColor,
    TextStyle? textStyle,
    EdgeInsets? padding,
    double? fontSize,
    BorderRadius? borderRadius,
    Duration? showDuration,
    VoidCallback? onDismissed,
  }) {
    final theme = Theme.of(context);
    final defaultColor = color ?? theme.colorScheme.secondary;
    final defaultTextColor = textColor ?? Colors.white;

    final overlay = Overlay.of(context);
    final entry = OverlayEntry(
      builder: (context) => Positioned(
        top: MediaQuery.of(context).size.height * 0.1,
        left: 0,
        right: 0,
        child: SafeArea(
          child: Center(
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 40),
              padding: padding ??
                  const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 12,
                  ),
              decoration: ShapeDecoration(
                color: defaultColor,
                shape: RoundedRectangleBorder(
                  borderRadius: borderRadius ?? BorderRadius.circular(8),
                ),
              ),
              child: Text(
                message,
                style: textStyle?.copyWith(color: defaultTextColor) ??
                    TextStyle(
                      color: defaultTextColor,
                      fontSize: fontSize ?? 14,
                    ),
                textAlign: TextAlign.center,
              ),
            ),
          ),
        ),
      ),
    );

    overlay.insert(entry);
    Future.delayed(showDuration ?? const Duration(seconds: 2), () {
      entry.remove();
      onDismissed?.call();
    });
  }
} 