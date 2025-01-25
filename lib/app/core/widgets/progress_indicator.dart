/// 进度指示器组件
class AppProgressIndicator extends StatelessWidget {
  final double? value;
  final Color? backgroundColor;
  final Color? color;
  final double strokeWidth;
  final String? label;
  final bool showPercentage;
  final double size;
  final bool linear;
  final Animation<Color?>? valueColor;
  final String? semanticsLabel;
  final String? semanticsValue;

  const AppProgressIndicator({
    super.key,
    this.value,
    this.backgroundColor,
    this.color,
    this.strokeWidth = 4.0,
    this.label,
    this.showPercentage = true,
    this.size = 36,
    this.linear = false,
    this.valueColor,
    this.semanticsLabel,
    this.semanticsValue,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultColor = color ?? theme.primaryColor;
    final defaultBackgroundColor = backgroundColor ?? theme.dividerColor;

    Widget indicator;
    if (linear) {
      indicator = LinearProgressIndicator(
        value: value,
        backgroundColor: defaultBackgroundColor,
        color: defaultColor,
        valueColor: valueColor,
        semanticsLabel: semanticsLabel,
        semanticsValue: semanticsValue,
      );
    } else {
      indicator = SizedBox.square(
        dimension: size,
        child: CircularProgressIndicator(
          value: value,
          backgroundColor: defaultBackgroundColor,
          color: defaultColor,
          strokeWidth: strokeWidth,
          valueColor: valueColor,
          semanticsLabel: semanticsLabel,
          semanticsValue: semanticsValue,
        ),
      );
    }

    if (label != null || (showPercentage && value != null)) {
      return Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          indicator,
          if (label != null || (showPercentage && value != null)) ...[
            const SizedBox(height: 8),
            Text(
              label ?? '${(value! * 100).toStringAsFixed(0)}%',
              style: theme.textTheme.bodyMedium,
            ),
          ],
        ],
      );
    }

    return indicator;
  }

  /// 创建加载指示器
  static Widget loading({
    String? message,
    Color? color,
    double size = 36,
    double strokeWidth = 4.0,
  }) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          AppProgressIndicator(
            size: size,
            color: color,
            strokeWidth: strokeWidth,
          ),
          if (message != null) ...[
            const SizedBox(height: 16),
            Text(message),
          ],
        ],
      ),
    );
  }
} 