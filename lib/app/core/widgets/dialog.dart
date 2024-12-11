/// 对话框组件
class AppDialog extends StatelessWidget {
  final String? title;
  final String? message;
  final Widget? content;
  final List<DialogAction>? actions;
  final bool barrierDismissible;
  final EdgeInsets? contentPadding;
  final EdgeInsets? actionsPadding;
  final MainAxisAlignment actionsAlignment;
  final bool showCloseButton;
  final double? maxWidth;
  final double? maxHeight;

  const AppDialog({
    super.key,
    this.title,
    this.message,
    this.content,
    this.actions,
    this.barrierDismissible = true,
    this.contentPadding,
    this.actionsPadding,
    this.actionsAlignment = MainAxisAlignment.end,
    this.showCloseButton = true,
    this.maxWidth,
    this.maxHeight,
  });

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxWidth: maxWidth ?? 400,
          maxHeight: maxHeight ?? MediaQuery.of(context).size.height * 0.8,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildHeader(context),
            if (message != null || content != null)
              Flexible(
                child: SingleChildScrollView(
                  padding: contentPadding ?? const EdgeInsets.all(24),
                  child: content ?? Text(message!),
                ),
              ),
            if (actions != null)
              Padding(
                padding: actionsPadding ??
                    const EdgeInsets.fromLTRB(24, 0, 24, 24),
                child: Row(
                  mainAxisAlignment: actionsAlignment,
                  children: actions!
                      .map((action) => Padding(
                            padding: const EdgeInsets.only(left: 16),
                            child: _buildAction(context, action),
                          ))
                      .toList(),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    if (title == null && !showCloseButton) return const SizedBox();

    return Container(
      padding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
      child: Row(
        children: [
          if (title != null)
            Expanded(
              child: Text(
                title!,
                style: Theme.of(context).textTheme.titleLarge,
              ),
            ),
          if (showCloseButton)
            IconButton(
              icon: const Icon(Icons.close),
              onPressed: () => Navigator.of(context).pop(),
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(),
            ),
        ],
      ),
    );
  }

  Widget _buildAction(BuildContext context, DialogAction action) {
    switch (action.style) {
      case DialogActionStyle.primary:
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
      case DialogActionStyle.secondary:
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
      case DialogActionStyle.text:
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

  /// 显示对话框
  static Future<T?> show<T>(
    BuildContext context, {
    String? title,
    String? message,
    Widget? content,
    List<DialogAction>? actions,
    bool barrierDismissible = true,
    EdgeInsets? contentPadding,
    EdgeInsets? actionsPadding,
    MainAxisAlignment actionsAlignment = MainAxisAlignment.end,
    bool showCloseButton = true,
    double? maxWidth,
    double? maxHeight,
  }) {
    return showDialog<T>(
      context: context,
      barrierDismissible: barrierDismissible,
      builder: (_) => AppDialog(
        title: title,
        message: message,
        content: content,
        actions: actions,
        barrierDismissible: barrierDismissible,
        contentPadding: contentPadding,
        actionsPadding: actionsPadding,
        actionsAlignment: actionsAlignment,
        showCloseButton: showCloseButton,
        maxWidth: maxWidth,
        maxHeight: maxHeight,
      ),
    );
  }

  /// 显示确认对话框
  static Future<bool?> confirm(
    BuildContext context, {
    String? title,
    required String message,
    String? confirmText,
    String? cancelText,
    DialogActionStyle confirmStyle = DialogActionStyle.primary,
    DialogActionStyle cancelStyle = DialogActionStyle.text,
  }) {
    return show<bool>(
      context,
      title: title,
      message: message,
      actions: [
        DialogAction(
          text: cancelText ?? '取消',
          style: cancelStyle,
          onPressed: () => Navigator.of(context).pop(false),
        ),
        DialogAction(
          text: confirmText ?? '确定',
          style: confirmStyle,
          onPressed: () => Navigator.of(context).pop(true),
        ),
      ],
    );
  }
}

/// 对话框按钮样式
enum DialogActionStyle {
  primary,
  secondary,
  text,
}

/// 对话框按钮
class DialogAction {
  final String text;
  final VoidCallback? onPressed;
  final DialogActionStyle style;
  final bool closeOnPressed;

  const DialogAction({
    required this.text,
    this.onPressed,
    this.style = DialogActionStyle.text,
    this.closeOnPressed = true,
  });
} 