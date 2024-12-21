import 'package:flutter/material.dart';

/// 按钮组件
class AppButton extends StatelessWidget {
  final String? text;
  final Widget? child;
  final VoidCallback? onPressed;
  final VoidCallback? onLongPress;
  final ButtonStyle? style;
  final bool loading;
  final Widget? loadingWidget;
  final double? width;
  final double? height;
  final double? minWidth;
  final double? minHeight;
  final EdgeInsets? padding;
  final BorderRadius? borderRadius;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final double? elevation;
  final bool disabled;
  
  const AppButton({
    super.key,
    this.text,
    this.child,
    this.onPressed,
    this.onLongPress,
    this.style,
    this.loading = false,
    this.loadingWidget,
    this.width,
    this.height,
    this.minWidth,
    this.minHeight,
    this.padding,
    this.borderRadius,
    this.backgroundColor,
    this.foregroundColor,
    this.elevation,
    this.disabled = false,
  }) : assert(text != null || child != null);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultLoadingWidget = SizedBox(
      width: 16,
      height: 16,
      child: CircularProgressIndicator(
        strokeWidth: 2,
        valueColor: AlwaysStoppedAnimation(
          foregroundColor ?? theme.primaryColor,
        ),
      ),
    );

    Widget buttonChild = loading
        ? loadingWidget ?? defaultLoadingWidget
        : child ?? Text(text!);

    return SizedBox(
      width: width,
      height: height,
      child: ElevatedButton(
        onPressed: (disabled || loading) ? null : onPressed,
        onLongPress: (disabled || loading) ? null : onLongPress,
        style: style ?? ElevatedButton.styleFrom(
          backgroundColor: backgroundColor,
          foregroundColor: foregroundColor,
          elevation: elevation,
          padding: padding,
          minimumSize: Size(minWidth ?? 0, minHeight ?? 0),
          shape: RoundedRectangleBorder(
            borderRadius: borderRadius ?? BorderRadius.circular(4),
          ),
        ),
        child: buttonChild,
      ),
    );
  }
}

/// 文本按钮组件
class AppTextButton extends AppButton {
  const AppTextButton({
    super.key,
    super.text,
    super.child,
    super.onPressed,
    super.onLongPress,
    super.style,
    super.loading = false,
    super.loadingWidget,
    super.width,
    super.height,
    super.minWidth,
    super.minHeight,
    super.padding,
    super.borderRadius,
    super.backgroundColor,
    super.foregroundColor,
    super.elevation = 0,
    super.disabled = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultLoadingWidget = SizedBox(
      width: 16,
      height: 16,
      child: CircularProgressIndicator(
        strokeWidth: 2,
        valueColor: AlwaysStoppedAnimation(
          foregroundColor ?? theme.primaryColor,
        ),
      ),
    );

    Widget buttonChild = loading
        ? loadingWidget ?? defaultLoadingWidget
        : child ?? Text(text!);

    return SizedBox(
      width: width,
      height: height,
      child: TextButton(
        onPressed: (disabled || loading) ? null : onPressed,
        onLongPress: (disabled || loading) ? null : onLongPress,
        style: style ?? TextButton.styleFrom(
          backgroundColor: backgroundColor,
          foregroundColor: foregroundColor,
          elevation: elevation,
          padding: padding,
          minimumSize: Size(minWidth ?? 0, minHeight ?? 0),
          shape: RoundedRectangleBorder(
            borderRadius: borderRadius ?? BorderRadius.circular(4),
          ),
        ),
        child: buttonChild,
      ),
    );
  }
}

/// 轮廓按钮组件
class AppOutlinedButton extends AppButton {
  final Color? borderColor;
  final double? borderWidth;
  
  const AppOutlinedButton({
    super.key,
    super.text,
    super.child,
    super.onPressed,
    super.onLongPress,
    super.style,
    super.loading = false,
    super.loadingWidget,
    super.width,
    super.height,
    super.minWidth,
    super.minHeight,
    super.padding,
    super.borderRadius,
    super.backgroundColor,
    super.foregroundColor,
    super.elevation = 0,
    super.disabled = false,
    this.borderColor,
    this.borderWidth,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultLoadingWidget = SizedBox(
      width: 16,
      height: 16,
      child: CircularProgressIndicator(
        strokeWidth: 2,
        valueColor: AlwaysStoppedAnimation(
          foregroundColor ?? theme.primaryColor,
        ),
      ),
    );

    Widget buttonChild = loading
        ? loadingWidget ?? defaultLoadingWidget
        : child ?? Text(text!);

    return SizedBox(
      width: width,
      height: height,
      child: OutlinedButton(
        onPressed: (disabled || loading) ? null : onPressed,
        onLongPress: (disabled || loading) ? null : onLongPress,
        style: style ?? OutlinedButton.styleFrom(
          backgroundColor: backgroundColor,
          foregroundColor: foregroundColor,
          elevation: elevation,
          padding: padding,
          minimumSize: Size(minWidth ?? 0, minHeight ?? 0),
          side: BorderSide(
            color: borderColor ?? theme.primaryColor,
            width: borderWidth ?? 1,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: borderRadius ?? BorderRadius.circular(4),
          ),
        ),
        child: buttonChild,
      ),
    );
  }
}

/// 图标按钮组件
class AppIconButton extends StatelessWidget {
  final IconData icon;
  final String? tooltip;
  final VoidCallback? onPressed;
  final double? size;
  final Color? color;
  final EdgeInsets? padding;
  
  const AppIconButton({
    super.key,
    required this.icon,
    this.tooltip,
    this.onPressed,
    this.size,
    this.color,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: Icon(icon),
      onPressed: onPressed,
      tooltip: tooltip,
      iconSize: size,
      color: color,
      padding: padding,
    );
  }
} 