/// 进度条组件
class ProgressBar extends StatelessWidget {
  final double value;
  final double? height;
  final Color? backgroundColor;
  final Color? progressColor;
  final List<Color>? progressColors;
  final BorderRadius? borderRadius;
  final BoxBorder? border;
  final List<BoxShadow>? shadows;
  final Widget? label;
  final EdgeInsets? padding;
  final bool showPercentage;
  final TextStyle? percentageStyle;
  final bool animated;
  final Duration animationDuration;
  final Curve animationCurve;
  final MainAxisAlignment alignment;
  final bool showValue;
  final String? valuePrefix;
  final String? valueSuffix;

  const ProgressBar({
    super.key,
    required this.value,
    this.height,
    this.backgroundColor,
    this.progressColor,
    this.progressColors,
    this.borderRadius,
    this.border,
    this.shadows,
    this.label,
    this.padding,
    this.showPercentage = false,
    this.percentageStyle,
    this.animated = true,
    this.animationDuration = const Duration(milliseconds: 300),
    this.animationCurve = Curves.easeInOut,
    this.alignment = MainAxisAlignment.start,
    this.showValue = false,
    this.valuePrefix,
    this.valueSuffix,
  }) : assert(value >= 0 && value <= 1);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultHeight = height ?? 4.0;
    final defaultBackgroundColor = backgroundColor ?? theme.dividerColor;
    final defaultProgressColor = progressColor ?? theme.primaryColor;

    Widget buildProgress(double width) {
      return Container(
        width: width,
        decoration: BoxDecoration(
          color: defaultProgressColor,
          gradient: progressColors != null
              ? LinearGradient(colors: progressColors!)
              : null,
          borderRadius: borderRadius,
        ),
      );
    }

    Widget progressBar = Container(
      height: defaultHeight,
      decoration: BoxDecoration(
        color: defaultBackgroundColor,
        borderRadius: borderRadius,
        border: border,
        boxShadow: shadows,
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final width = constraints.maxWidth * value;
          return animated
              ? AnimatedContainer(
                  duration: animationDuration,
                  curve: animationCurve,
                  child: buildProgress(width),
                )
              : buildProgress(width);
        },
      ),
    );

    final hasLabel = label != null || showPercentage || showValue;
    if (hasLabel) {
      final percentage = (value * 100).toInt();
      final valueText = [
        if (valuePrefix != null) valuePrefix!,
        if (showPercentage) '$percentage%',
        if (showValue) value.toString(),
        if (valueSuffix != null) valueSuffix!,
      ].join();

      progressBar = Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          if (label != null) ...[
            label!,
            const SizedBox(height: 8),
          ],
          Row(
            children: [
              Expanded(child: progressBar),
              if (showPercentage || showValue) ...[
                const SizedBox(width: 8),
                Text(
                  valueText,
                  style: percentageStyle ??
                      theme.textTheme.bodySmall?.copyWith(
                        color: theme.primaryColor,
                      ),
                ),
              ],
            ],
          ),
        ],
      );
    }

    if (padding != null) {
      progressBar = Padding(
        padding: padding!,
        child: progressBar,
      );
    }

    return progressBar;
  }
} 