/// 步骤条组件
class StepBar extends StatelessWidget {
  final List<StepItem> steps;
  final int currentStep;
  final Color? activeColor;
  final Color? inactiveColor;
  final double? height;
  final double? spacing;
  final bool showLabel;
  final TextStyle? labelStyle;
  final TextStyle? activeStyle;
  final TextStyle? inactiveStyle;

  const StepBar({
    super.key,
    required this.steps,
    this.currentStep = 0,
    this.activeColor,
    this.inactiveColor,
    this.height,
    this.spacing,
    this.showLabel = true,
    this.labelStyle,
    this.activeStyle,
    this.inactiveStyle,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultActiveColor = activeColor ?? theme.primaryColor;
    final defaultInactiveColor = inactiveColor ?? theme.disabledColor;
    final defaultHeight = height ?? 32.0;
    final defaultSpacing = spacing ?? 8.0;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          height: defaultHeight,
          child: Row(
            children: List.generate(steps.length * 2 - 1, (index) {
              // 步骤点
              if (index.isEven) {
                final stepIndex = index ~/ 2;
                final step = steps[stepIndex];
                final isActive = stepIndex <= currentStep;

                return Container(
                  width: defaultHeight,
                  height: defaultHeight,
                  decoration: BoxDecoration(
                    color: isActive ? defaultActiveColor : defaultInactiveColor,
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: Text(
                      '${stepIndex + 1}',
                      style: (isActive ? activeStyle : inactiveStyle) ??
                          TextStyle(
                            color: Colors.white,
                            fontSize: defaultHeight * 0.5,
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ),
                );
              }
              // 连接线
              else {
                final stepIndex = index ~/ 2;
                final isActive = stepIndex < currentStep;

                return Expanded(
                  child: Container(
                    height: 2,
                    color: isActive ? defaultActiveColor : defaultInactiveColor,
                  ),
                );
              }
            }),
          ),
        ),
        if (showLabel) ...[
          SizedBox(height: defaultSpacing),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: steps.map((step) {
              final index = steps.indexOf(step);
              final isActive = index <= currentStep;

              return Expanded(
                child: Text(
                  step.label,
                  style: labelStyle ??
                      theme.textTheme.bodySmall?.copyWith(
                        color: isActive ? defaultActiveColor : defaultInactiveColor,
                      ),
                  textAlign: TextAlign.center,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              );
            }).toList(),
          ),
        ],
      ],
    );
  }
}

/// 步骤项
class StepItem {
  final String label;
  final String? description;

  const StepItem({
    required this.label,
    this.description,
  });
} 