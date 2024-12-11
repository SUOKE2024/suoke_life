/// 底部弹出组件
class AppBottomSheet extends StatelessWidget {
  final String? title;
  final Widget? child;
  final List<BottomSheetAction>? actions;
  final EdgeInsets? padding;
  final double? maxHeight;
  final bool showCloseButton;
  final bool showDragHandle;
  final bool isDismissible;
  final bool enableDrag;
  final Color? backgroundColor;
  final BorderRadius? borderRadius;

  const AppBottomSheet({
    super.key,
    this.title,
    this.child,
    this.actions,
    this.padding,
    this.maxHeight,
    this.showCloseButton = true,
    this.showDragHandle = true,
    this.isDismissible = true,
    this.enableDrag = true,
    this.backgroundColor,
    this.borderRadius,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      constraints: BoxConstraints(
        maxHeight: maxHeight ?? MediaQuery.of(context).size.height * 0.85,
      ),
      decoration: BoxDecoration(
        color: backgroundColor ?? theme.scaffoldBackgroundColor,
        borderRadius: borderRadius ??
            const BorderRadius.vertical(top: Radius.circular(16)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (showDragHandle)
            Container(
              width: 32,
              height: 4,
              margin: const EdgeInsets.symmetric(vertical: 8),
              decoration: BoxDecoration(
                color: theme.dividerColor,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          if (title != null || showCloseButton)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
              child: Row(
                children: [
                  if (title != null)
                    Expanded(
                      child: Text(
                        title!,
                        style: theme.textTheme.titleLarge,
                      ),
                    ),
                  if (showCloseButton)
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                ],
              ),
            ),
          if (child != null)
            Flexible(
              child: SingleChildScrollView(
                padding: padding ?? const EdgeInsets.all(16),
                child: child,
              ),
            ),
          if (actions != null) ...[
            const Divider(height: 1),
            SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: actions!
                      .map((action) => Padding(
                            padding: const EdgeInsets.only(left: 16),
                            child: _buildAction(context, action),
                          ))
                      .toList(),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildAction(BuildContext context, BottomSheetAction action) {
    switch (action.style) {
      case BottomSheetActionStyle.primary:
        return ElevatedButton(
          onPressed: () {
            if (action.onPressed != null) {
              action.onPressed!();
            }
            if (action.closeOnPressed) {
              Navigator.of(context).pop();
            }
          },
          child: Text(action.text),
        );
      case BottomSheetActionStyle.secondary:
        return OutlinedButton(
          onPressed: () {
            if (action.onPressed != null) {
              action.onPressed!();
            }
            if (action.closeOnPressed) {
              Navigator.of(context).pop();
            }
          },
          child: Text(action.text),
        );
      case BottomSheetActionStyle.text:
        return TextButton(
          onPressed: () {
            if (action.onPressed != null) {
              action.onPressed!();
            }
            if (action.closeOnPressed) {
              Navigator.of(context).pop();
            }
          },
          child: Text(action.text),
        );
    }
  }

  /// 显示底部弹出框
  static Future<T?> show<T>(
    BuildContext context, {
    String? title,
    Widget? child,
    List<BottomSheetAction>? actions,
    EdgeInsets? padding,
    double? maxHeight,
    bool showCloseButton = true,
    bool showDragHandle = true,
    bool isDismissible = true,
    bool enableDrag = true,
    Color? backgroundColor,
    BorderRadius? borderRadius,
  }) {
    return showModalBottomSheet<T>(
      context: context,
      isDismissible: isDismissible,
      enableDrag: enableDrag,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (_) => AppBottomSheet(
        title: title,
        child: child,
        actions: actions,
        padding: padding,
        maxHeight: maxHeight,
        showCloseButton: showCloseButton,
        showDragHandle: showDragHandle,
        isDismissible: isDismissible,
        enableDrag: enableDrag,
        backgroundColor: backgroundColor,
        borderRadius: borderRadius,
      ),
    );
  }
}

/// 底部弹出框按钮样式
enum BottomSheetActionStyle {
  primary,
  secondary,
  text,
}

/// 底部弹出框按钮
class BottomSheetAction {
  final String text;
  final VoidCallback? onPressed;
  final BottomSheetActionStyle style;
  final bool closeOnPressed;

  const BottomSheetAction({
    required this.text,
    this.onPressed,
    this.style = BottomSheetActionStyle.text,
    this.closeOnPressed = true,
  });
} 