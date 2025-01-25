import 'package:flutter/material.dart';

/// 对话框组件
class AppDialog extends StatelessWidget {
  final String? title;
  final Widget? titleWidget;
  final String? content;
  final Widget? contentWidget;
  final List<Widget>? actions;
  final EdgeInsets? padding;
  final EdgeInsets? contentPadding;
  final EdgeInsets? actionsPadding;
  final Color? backgroundColor;
  final double? elevation;
  final BorderRadius? borderRadius;
  final bool barrierDismissible;
  
  const AppDialog({
    super.key,
    this.title,
    this.titleWidget,
    this.content,
    this.contentWidget,
    this.actions,
    this.padding,
    this.contentPadding,
    this.actionsPadding,
    this.backgroundColor,
    this.elevation,
    this.borderRadius,
    this.barrierDismissible = true,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: titleWidget ?? (title != null ? Text(title!) : null),
      content: contentWidget ?? (content != null ? Text(content!) : null),
      actions: actions,
      contentPadding: contentPadding ?? const EdgeInsets.fromLTRB(24, 20, 24, 24),
      actionsPadding: actionsPadding ?? const EdgeInsets.fromLTRB(24, 0, 24, 16),
      backgroundColor: backgroundColor,
      elevation: elevation,
      shape: RoundedRectangleBorder(
        borderRadius: borderRadius ?? BorderRadius.circular(8),
      ),
    );
  }

  /// 显示对话框
  static Future<T?> show<T>({
    required BuildContext context,
    String? title,
    Widget? titleWidget,
    String? content,
    Widget? contentWidget,
    List<Widget>? actions,
    EdgeInsets? padding,
    EdgeInsets? contentPadding,
    EdgeInsets? actionsPadding,
    Color? backgroundColor,
    double? elevation,
    BorderRadius? borderRadius,
    bool barrierDismissible = true,
  }) {
    return showDialog<T>(
      context: context,
      barrierDismissible: barrierDismissible,
      builder: (context) => AppDialog(
        title: title,
        titleWidget: titleWidget,
        content: content,
        contentWidget: contentWidget,
        actions: actions,
        padding: padding,
        contentPadding: contentPadding,
        actionsPadding: actionsPadding,
        backgroundColor: backgroundColor,
        elevation: elevation,
        borderRadius: borderRadius,
        barrierDismissible: barrierDismissible,
      ),
    );
  }
}

/// 确认对话框组件
class AppConfirmDialog extends StatelessWidget {
  final String? title;
  final Widget? titleWidget;
  final String? content;
  final Widget? contentWidget;
  final String? confirmText;
  final String? cancelText;
  final VoidCallback? onConfirm;
  final VoidCallback? onCancel;
  final Color? confirmColor;
  final Color? cancelColor;
  final EdgeInsets? padding;
  final EdgeInsets? contentPadding;
  final EdgeInsets? actionsPadding;
  final Color? backgroundColor;
  final double? elevation;
  final BorderRadius? borderRadius;
  final bool barrierDismissible;
  
  const AppConfirmDialog({
    super.key,
    this.title,
    this.titleWidget,
    this.content,
    this.contentWidget,
    this.confirmText,
    this.cancelText,
    this.onConfirm,
    this.onCancel,
    this.confirmColor,
    this.cancelColor,
    this.padding,
    this.contentPadding,
    this.actionsPadding,
    this.backgroundColor,
    this.elevation,
    this.borderRadius,
    this.barrierDismissible = true,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return AppDialog(
      title: title,
      titleWidget: titleWidget,
      content: content,
      contentWidget: contentWidget,
      actions: [
        TextButton(
          onPressed: () {
            Navigator.pop(context);
            onCancel?.call();
          },
          child: Text(
            cancelText ?? '取消',
            style: TextStyle(color: cancelColor),
          ),
        ),
        TextButton(
          onPressed: () {
            Navigator.pop(context);
            onConfirm?.call();
          },
          child: Text(
            confirmText ?? '确定',
            style: TextStyle(
              color: confirmColor ?? theme.primaryColor,
            ),
          ),
        ),
      ],
      padding: padding,
      contentPadding: contentPadding,
      actionsPadding: actionsPadding,
      backgroundColor: backgroundColor,
      elevation: elevation,
      borderRadius: borderRadius,
      barrierDismissible: barrierDismissible,
    );
  }

  /// 显示确认对话框
  static Future<bool> show({
    required BuildContext context,
    String? title,
    Widget? titleWidget,
    String? content,
    Widget? contentWidget,
    String? confirmText,
    String? cancelText,
    VoidCallback? onConfirm,
    VoidCallback? onCancel,
    Color? confirmColor,
    Color? cancelColor,
    EdgeInsets? padding,
    EdgeInsets? contentPadding,
    EdgeInsets? actionsPadding,
    Color? backgroundColor,
    double? elevation,
    BorderRadius? borderRadius,
    bool barrierDismissible = true,
  }) async {
    final result = await showDialog<bool>(
      context: context,
      barrierDismissible: barrierDismissible,
      builder: (context) => AppConfirmDialog(
        title: title,
        titleWidget: titleWidget,
        content: content,
        contentWidget: contentWidget,
        confirmText: confirmText,
        cancelText: cancelText,
        onConfirm: onConfirm,
        onCancel: onCancel,
        confirmColor: confirmColor,
        cancelColor: cancelColor,
        padding: padding,
        contentPadding: contentPadding,
        actionsPadding: actionsPadding,
        backgroundColor: backgroundColor,
        elevation: elevation,
        borderRadius: borderRadius,
        barrierDismissible: barrierDismissible,
      ),
    );
    return result ?? false;
  }
} 