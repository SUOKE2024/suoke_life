import 'package:flutter/material.dart';

/// 底部弹出组件
class AppBottomSheet extends StatelessWidget {
  final Widget child;
  final String? title;
  final Widget? titleWidget;
  final List<Widget>? actions;
  final EdgeInsets? padding;
  final double? height;
  final bool showDragHandle;
  final bool showCloseButton;
  final VoidCallback? onClose;
  final Color? backgroundColor;
  final double? borderRadius;

  const AppBottomSheet({
    super.key,
    required this.child,
    this.title,
    this.titleWidget,
    this.actions,
    this.padding,
    this.height,
    this.showDragHandle = true,
    this.showCloseButton = true,
    this.onClose,
    this.backgroundColor,
    this.borderRadius,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      height: height,
      decoration: BoxDecoration(
        color: backgroundColor ?? theme.scaffoldBackgroundColor,
        borderRadius: BorderRadius.vertical(
          top: Radius.circular(borderRadius ?? 16),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (showDragHandle)
            Container(
              width: 32,
              height: 4,
              margin: const EdgeInsets.symmetric(vertical: 12),
              decoration: BoxDecoration(
                color: theme.dividerColor,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          if (title != null || titleWidget != null || showCloseButton)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 8, 8),
              child: Row(
                children: [
                  Expanded(
                    child: DefaultTextStyle(
                      style: theme.textTheme.titleLarge!,
                      child: titleWidget ?? Text(title ?? ''),
                    ),
                  ),
                  if (showCloseButton)
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: () {
                        Navigator.of(context).pop();
                        onClose?.call();
                      },
                    ),
                ],
              ),
            ),
          Expanded(
            child: Padding(
              padding: padding ?? const EdgeInsets.all(16),
              child: child,
            ),
          ),
          if (actions != null)
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: actions!,
              ),
            ),
        ],
      ),
    );
  }

  /// 显示底部弹出
  static Future<T?> show<T>({
    required BuildContext context,
    required Widget child,
    String? title,
    Widget? titleWidget,
    List<Widget>? actions,
    EdgeInsets? padding,
    double? height,
    bool showDragHandle = true,
    bool showCloseButton = true,
    VoidCallback? onClose,
    Color? backgroundColor,
    double? borderRadius,
    bool isDismissible = true,
    bool enableDrag = true,
  }) {
    return showModalBottomSheet<T>(
      context: context,
      isDismissible: isDismissible,
      enableDrag: enableDrag,
      backgroundColor: Colors.transparent,
      builder: (context) => AppBottomSheet(
        title: title,
        titleWidget: titleWidget,
        actions: actions,
        padding: padding,
        height: height,
        showDragHandle: showDragHandle,
        showCloseButton: showCloseButton,
        onClose: onClose,
        backgroundColor: backgroundColor,
        borderRadius: borderRadius,
        child: child,
      ),
    );
  }
}
