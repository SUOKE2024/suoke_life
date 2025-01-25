import 'package:flutter/material.dart';

/// 步骤条组件
class AppStepper extends StatelessWidget {
  final List<AppStepItem> steps;
  final int currentStep;
  final ValueChanged<int>? onStepTapped;
  final VoidCallback? onStepContinue;
  final VoidCallback? onStepCancel;
  final bool vertical;
  final Color? activeColor;
  final Color? inactiveColor;
  final TextStyle? titleStyle;
  final TextStyle? subtitleStyle;
  final EdgeInsets? margin;
  
  const AppStepper({
    super.key,
    required this.steps,
    required this.currentStep,
    this.onStepTapped,
    this.onStepContinue,
    this.onStepCancel,
    this.vertical = true,
    this.activeColor,
    this.inactiveColor,
    this.titleStyle,
    this.subtitleStyle,
    this.margin,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultActiveColor = activeColor ?? theme.primaryColor;
    final defaultInactiveColor = inactiveColor ?? theme.unselectedWidgetColor;

    return Stepper(
      steps: steps.map((step) {
        return Step(
          title: Text(
            step.title,
            style: titleStyle?.copyWith(
              color: step.isActive ? defaultActiveColor : defaultInactiveColor,
            ) ?? TextStyle(
              color: step.isActive ? defaultActiveColor : defaultInactiveColor,
            ),
          ),
          subtitle: step.subtitle != null ? Text(
            step.subtitle!,
            style: subtitleStyle?.copyWith(
              color: step.isActive ? defaultActiveColor : defaultInactiveColor,
            ),
          ) : null,
          content: step.content,
          state: step.state,
          isActive: step.isActive,
        );
      }).toList(),
      currentStep: currentStep,
      onStepTapped: onStepTapped,
      onStepContinue: onStepContinue,
      onStepCancel: onStepCancel,
      type: vertical ? StepperType.vertical : StepperType.horizontal,
      margin: margin,
    );
  }
}

/// 步骤项
class AppStepItem {
  final String title;
  final String? subtitle;
  final Widget content;
  final StepState state;
  final bool isActive;
  
  const AppStepItem({
    required this.title,
    this.subtitle,
    required this.content,
    this.state = StepState.indexed,
    this.isActive = false,
  });
} 