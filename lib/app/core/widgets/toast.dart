import 'package:flutter/material.dart';

/// Toast组件
class AppToast extends StatelessWidget {
  final String message;
  final Color? backgroundColor;
  final Color? textColor;
  final double? fontSize;
  final EdgeInsets? padding;
  final BorderRadius? borderRadius;
  final Duration? duration;
  
  const AppToast({
    super.key,
    required this.message,
    this.backgroundColor,
    this.textColor,
    this.fontSize,
    this.padding,
    this.borderRadius,
    this.duration,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Container(
      padding: padding ?? const EdgeInsets.symmetric(
        horizontal: 24,
        vertical: 12,
      ),
      decoration: BoxDecoration(
        color: backgroundColor ?? Colors.black87,
        borderRadius: borderRadius ?? BorderRadius.circular(8),
      ),
      child: Text(
        message,
        style: TextStyle(
          color: textColor ?? Colors.white,
          fontSize: fontSize ?? 14,
        ),
      ),
    );
  }

  /// 显示Toast
  static void show(
    BuildContext context,
    String message, {
    Color? backgroundColor,
    Color? textColor,
    double? fontSize,
    EdgeInsets? padding,
    BorderRadius? borderRadius,
    Duration? duration,
    VoidCallback? onDismissed,
  }) {
    final overlay = Overlay.of(context);
    final entry = OverlayEntry(
      builder: (context) => Positioned(
        top: MediaQuery.of(context).size.height * 0.1,
        left: 0,
        right: 0,
        child: SafeArea(
          child: Center(
            child: AppToast(
              message: message,
              backgroundColor: backgroundColor,
              textColor: textColor,
              fontSize: fontSize,
              padding: padding,
              borderRadius: borderRadius,
              duration: duration,
            ),
          ),
        ),
      ),
    );

    overlay.insert(entry);
    Future.delayed(duration ?? const Duration(seconds: 2), () {
      entry.remove();
      onDismissed?.call();
    });
  }
} 