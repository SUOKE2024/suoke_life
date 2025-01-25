/// 按钮组件
class AppButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool loading;
  final bool outlined;
  final IconData? icon;
  final Color? color;
  final double? width;
  final double height;
  final double borderRadius;

  const AppButton({
    super.key,
    required this.text,
    this.onPressed,
    this.loading = false,
    this.outlined = false,
    this.icon,
    this.color,
    this.width,
    this.height = 48,
    this.borderRadius = 8,
  });

  @override
  Widget build(BuildContext context) {
    final style = outlined
        ? OutlinedButton.styleFrom(
            foregroundColor: color ?? Theme.of(context).primaryColor,
            side: BorderSide(
              color: color ?? Theme.of(context).primaryColor,
            ),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(borderRadius),
            ),
          )
        : ElevatedButton.styleFrom(
            backgroundColor: color ?? Theme.of(context).primaryColor,
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(borderRadius),
            ),
          );

    final child = loading
        ? const SizedBox.square(
            dimension: 24,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation(Colors.white),
            ),
          )
        : Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (icon != null) ...[
                Icon(icon, size: 20),
                const SizedBox(width: 8),
              ],
              Text(text),
            ],
          );

    final button = outlined
        ? OutlinedButton(
            onPressed: loading ? null : onPressed,
            style: style,
            child: child,
          )
        : ElevatedButton(
            onPressed: loading ? null : onPressed,
            style: style,
            child: child,
          );

    return SizedBox(
      width: width,
      height: height,
      child: button,
    );
  }
} 