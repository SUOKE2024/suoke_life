import 'package:flutter/material.dart';

/// 空状态组件
class AppEmpty extends StatelessWidget {
  final String? message;
  final Widget? image;
  final Widget? action;
  final EdgeInsets padding;
  
  const AppEmpty({
    super.key,
    this.message,
    this.image,
    this.action,
    this.padding = const EdgeInsets.all(32),
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultColor = theme.disabledColor;
    final defaultStyle = theme.textTheme.bodyLarge?.copyWith(
      color: theme.disabledColor,
    );

    return Center(
      child: Padding(
        padding: padding,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (image != null) ...[
              image!,
              const SizedBox(height: 16),
            ],
            if (message != null) ...[
              Text(
                message!,
                style: defaultStyle,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
            ],
            if (action != null) ...[
              action!,
            ],
          ],
        ),
      ),
    );
  }
} 