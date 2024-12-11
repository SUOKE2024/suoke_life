/// 步进器组件
class AppStepper extends StatelessWidget {
  final List<StepItem> steps;
  final int currentStep;
  final ValueChanged<int>? onStepTapped;
  final VoidCallback? onStepContinue;
  final VoidCallback? onStepCancel;
  final Widget Function(BuildContext, StepItem)? stepBuilder;
  final bool vertical;
  final Color? activeColor;
  final Color? inactiveColor;
  final String? continueText;
  final String? cancelText;

  const AppStepper({
    super.key,
    required this.steps,
    this.currentStep = 0,
    this.onStepTapped,
    this.onStepContinue,
    this.onStepCancel,
    this.stepBuilder,
    this.vertical = true,
    this.activeColor,
    this.inactiveColor,
    this.continueText,
    this.cancelText,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultActiveColor = activeColor ?? theme.primaryColor;
    final defaultInactiveColor = inactiveColor ?? theme.disabledColor;

    if (!vertical) {
      return Column(
        children: [
          Row(
            children: List.generate(steps.length * 2 - 1, (index) {
              if (index.isOdd) {
                return Expanded(
                  child: Container(
                    height: 1,
                    color: index ~/ 2 < currentStep
                        ? defaultActiveColor
                        : defaultInactiveColor,
                  ),
                );
              }
              final step = steps[index ~/ 2];
              final isActive = index ~/ 2 == currentStep;
              final isCompleted = index ~/ 2 < currentStep;
              return _buildHorizontalStep(
                context,
                step,
                isActive,
                isCompleted,
                index ~/ 2,
              );
            }),
          ),
          const SizedBox(height: 16),
          _buildControls(context),
        ],
      );
    }

    return Column(
      children: [
        ...List.generate(steps.length, (index) {
          final step = steps[index];
          final isActive = index == currentStep;
          final isCompleted = index < currentStep;
          return _buildVerticalStep(
            context,
            step,
            isActive,
            isCompleted,
            index,
            isLast: index == steps.length - 1,
          );
        }),
        _buildControls(context),
      ],
    );
  }

  Widget _buildHorizontalStep(
    BuildContext context,
    StepItem step,
    bool isActive,
    bool isCompleted,
    int index,
  ) {
    final theme = Theme.of(context);
    final color = isActive || isCompleted
        ? activeColor ?? theme.primaryColor
        : inactiveColor ?? theme.disabledColor;

    return GestureDetector(
      onTap: onStepTapped != null ? () => onStepTapped!(index) : null,
      child: Column(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isCompleted ? color : Colors.transparent,
              border: Border.all(
                color: color,
                width: 2,
              ),
            ),
            child: Center(
              child: isCompleted
                  ? const Icon(
                      Icons.check,
                      color: Colors.white,
                      size: 18,
                    )
                  : Text(
                      '${index + 1}',
                      style: TextStyle(color: color),
                    ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            step.title,
            style: theme.textTheme.bodySmall?.copyWith(
              color: color,
              fontWeight: isActive ? FontWeight.bold : null,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVerticalStep(
    BuildContext context,
    StepItem step,
    bool isActive,
    bool isCompleted,
    int index, {
    bool isLast = false,
  }) {
    if (stepBuilder != null) {
      return stepBuilder!(context, step);
    }

    final theme = Theme.of(context);
    final color = isActive || isCompleted
        ? activeColor ?? theme.primaryColor
        : inactiveColor ?? theme.disabledColor;

    return Column(
      children: [
        InkWell(
          onTap: onStepTapped != null ? () => onStepTapped!(index) : null,
          child: Row(
            children: [
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: isCompleted ? color : Colors.transparent,
                  border: Border.all(
                    color: color,
                    width: 2,
                  ),
                ),
                child: Center(
                  child: isCompleted
                      ? const Icon(
                          Icons.check,
                          color: Colors.white,
                          size: 18,
                        )
                      : Text(
                          '${index + 1}',
                          style: TextStyle(color: color),
                        ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      step.title,
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: color,
                        fontWeight: isActive ? FontWeight.bold : null,
                      ),
                    ),
                    if (step.subtitle != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        step.subtitle!,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: color.withOpacity(0.8),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
        if (!isLast)
          Container(
            margin: const EdgeInsets.only(left: 16),
            width: 2,
            height: 32,
            color: isCompleted ? color : defaultInactiveColor,
          ),
      ],
    );
  }

  Widget _buildControls(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          if (currentStep > 0)
            TextButton(
              onPressed: onStepCancel,
              child: Text(cancelText ?? '上一步'),
            ),
          if (currentStep < steps.length - 1) ...[
            const SizedBox(width: 16),
            ElevatedButton(
              onPressed: onStepContinue,
              child: Text(continueText ?? '下一步'),
            ),
          ],
        ],
      ),
    );
  }
}

/// 步骤项
class StepItem {
  final String title;
  final String? subtitle;
  final Widget? content;

  const StepItem({
    required this.title,
    this.subtitle,
    this.content,
  });
} 