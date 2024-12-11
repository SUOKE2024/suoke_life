/// 加载组件
class AppLoading extends StatelessWidget {
  final String? message;
  final Color? color;
  final double size;
  final double strokeWidth;
  final bool overlay;
  final Color? backgroundColor;
  final Widget? indicator;
  final EdgeInsets? padding;
  final MainAxisAlignment alignment;

  const AppLoading({
    super.key,
    this.message,
    this.color,
    this.size = 36,
    this.strokeWidth = 4,
    this.overlay = false,
    this.backgroundColor,
    this.indicator,
    this.padding,
    this.alignment = MainAxisAlignment.center,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultColor = color ?? theme.primaryColor;

    Widget child = Column(
      mainAxisAlignment: alignment,
      mainAxisSize: MainAxisSize.min,
      children: [
        indicator ??
            SizedBox.square(
              dimension: size,
              child: CircularProgressIndicator(
                strokeWidth: strokeWidth,
                valueColor: AlwaysStoppedAnimation(defaultColor),
              ),
            ),
        if (message != null) ...[
          const SizedBox(height: 16),
          Text(
            message!,
            style: theme.textTheme.bodyMedium?.copyWith(color: defaultColor),
          ),
        ],
      ],
    );

    if (padding != null) {
      child = Padding(padding: padding!, child: child);
    }

    if (overlay) {
      return Container(
        color: backgroundColor ?? Colors.black26,
        alignment: Alignment.center,
        child: child,
      );
    }

    return child;
  }

  /// 显示全屏加载
  static Future<T?> show<T>(
    BuildContext context, {
    String? message,
    Color? color,
    double size = 36,
    double strokeWidth = 4,
    Color? backgroundColor,
    Widget? indicator,
    EdgeInsets? padding,
    MainAxisAlignment alignment = MainAxisAlignment.center,
    bool barrierDismissible = false,
  }) {
    return showDialog<T>(
      context: context,
      barrierDismissible: barrierDismissible,
      barrierColor: Colors.transparent,
      builder: (_) => WillPopScope(
        onWillPop: () async => barrierDismissible,
        child: AppLoading(
          message: message,
          color: color,
          size: size,
          strokeWidth: strokeWidth,
          overlay: true,
          backgroundColor: backgroundColor,
          indicator: indicator,
          padding: padding,
          alignment: alignment,
        ),
      ),
    );
  }
} 