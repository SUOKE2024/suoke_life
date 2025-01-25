import 'package:flutter/material.dart';

/// 文字提示组件
class AppTooltip extends StatelessWidget {
  final Widget child;
  final String message;
  final double? height;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final double? verticalOffset;
  final bool? preferBelow;
  final bool? excludeFromSemantics;
  final Decoration? decoration;
  final TextStyle? textStyle;
  final Duration? waitDuration;
  final Duration? showDuration;
  final TooltipTriggerMode? triggerMode;
  final bool? enableFeedback;
  
  const AppTooltip({
    super.key,
    required this.child,
    required this.message,
    this.height,
    this.padding,
    this.margin,
    this.verticalOffset,
    this.preferBelow,
    this.excludeFromSemantics,
    this.decoration,
    this.textStyle,
    this.waitDuration,
    this.showDuration,
    this.triggerMode,
    this.enableFeedback,
  });

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: message,
      height: height,
      padding: padding,
      margin: margin,
      verticalOffset: verticalOffset,
      preferBelow: preferBelow,
      excludeFromSemantics: excludeFromSemantics,
      decoration: decoration,
      textStyle: textStyle,
      waitDuration: waitDuration,
      showDuration: showDuration,
      triggerMode: triggerMode,
      enableFeedback: enableFeedback,
      child: child,
    );
  }
} 