import 'package:flutter/material.dart';

class LoadingButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final Widget child;
  final bool isLoading;
  final double? width;
  final double? height;
  final EdgeInsetsGeometry? padding;
  final double? borderRadius;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final double? elevation;
  final Size? minimumSize;
  final Size? maximumSize;
  final BorderSide? side;
  final OutlinedBorder? shape;
  final MouseCursor? mouseCursor;
  final MaterialTapTargetSize? tapTargetSize;
  final Duration? animationDuration;
  final bool? enableFeedback;
  final AlignmentGeometry? alignment;
  final InteractiveInkFeatureFactory? splashFactory;

  const LoadingButton({
    Key? key,
    required this.onPressed,
    required this.child,
    this.isLoading = false,
    this.width,
    this.height,
    this.padding,
    this.borderRadius,
    this.backgroundColor,
    this.foregroundColor,
    this.elevation,
    this.minimumSize,
    this.maximumSize,
    this.side,
    this.shape,
    this.mouseCursor,
    this.tapTargetSize,
    this.animationDuration,
    this.enableFeedback,
    this.alignment,
    this.splashFactory,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return SizedBox(
      width: width,
      height: height,
      child: ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: backgroundColor,
          foregroundColor: foregroundColor,
          elevation: elevation,
          padding: padding,
          minimumSize: minimumSize,
          maximumSize: maximumSize,
          side: side,
          shape: shape ?? RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(borderRadius ?? 8),
          ),
          mouseCursor: mouseCursor,
          tapTargetSize: tapTargetSize,
          animationDuration: animationDuration,
          enableFeedback: enableFeedback,
          alignment: alignment,
          splashFactory: splashFactory,
          disabledBackgroundColor: backgroundColor?.withOpacity(0.6) ?? 
              theme.colorScheme.primary.withOpacity(0.6),
          disabledForegroundColor: foregroundColor?.withOpacity(0.6) ?? 
              theme.colorScheme.onPrimary.withOpacity(0.6),
        ),
        child: isLoading
            ? SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    foregroundColor ?? theme.colorScheme.onPrimary,
                  ),
                ),
              )
            : child,
      ),
    );
  }
} 