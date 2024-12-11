/// 空状态组件
class AppEmpty extends StatelessWidget {
  final String? message;
  final String? description;
  final Widget? icon;
  final Widget? image;
  final List<Widget>? actions;
  final EdgeInsets? padding;
  final double? spacing;
  final MainAxisAlignment alignment;
  final TextStyle? messageStyle;
  final TextStyle? descriptionStyle;

  const AppEmpty({
    super.key,
    this.message,
    this.description,
    this.icon,
    this.image,
    this.actions,
    this.padding,
    this.spacing,
    this.alignment = MainAxisAlignment.center,
    this.messageStyle,
    this.descriptionStyle,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultSpacing = spacing ?? 16.0;

    return Container(
      padding: padding ?? const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: alignment,
        children: [
          if (image != null)
            Padding(
              padding: EdgeInsets.only(bottom: defaultSpacing),
              child: image,
            )
          else if (icon != null)
            Padding(
              padding: EdgeInsets.only(bottom: defaultSpacing),
              child: icon,
            )
          else
            Padding(
              padding: EdgeInsets.only(bottom: defaultSpacing),
              child: Icon(
                Icons.inbox_outlined,
                size: 64,
                color: theme.disabledColor,
              ),
            ),
          if (message != null)
            Padding(
              padding: EdgeInsets.only(bottom: defaultSpacing / 2),
              child: Text(
                message!,
                style: messageStyle ??
                    theme.textTheme.titleMedium?.copyWith(
                      color: theme.disabledColor,
                    ),
                textAlign: TextAlign.center,
              ),
            ),
          if (description != null)
            Padding(
              padding: EdgeInsets.only(bottom: defaultSpacing),
              child: Text(
                description!,
                style: descriptionStyle ??
                    theme.textTheme.bodyMedium?.copyWith(
                      color: theme.disabledColor,
                    ),
                textAlign: TextAlign.center,
              ),
            ),
          if (actions != null) ...[
            SizedBox(height: defaultSpacing),
            ...actions!,
          ],
        ],
      ),
    );
  }
} 