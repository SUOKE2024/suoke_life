/// 分割线组件
class AppDivider extends StatelessWidget {
  final double height;
  final double thickness;
  final double? indent;
  final double? endIndent;
  final Color? color;
  final String? text;
  final TextStyle? textStyle;
  final EdgeInsets? padding;
  final bool vertical;
  final MainAxisAlignment alignment;

  const AppDivider({
    super.key,
    this.height = 16,
    this.thickness = 1,
    this.indent,
    this.endIndent,
    this.color,
    this.text,
    this.textStyle,
    this.padding,
    this.vertical = false,
    this.alignment = MainAxisAlignment.center,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultColor = color ?? theme.dividerColor;

    if (text == null) {
      return vertical
          ? VerticalDivider(
              width: height,
              thickness: thickness,
              indent: indent,
              endIndent: endIndent,
              color: defaultColor,
            )
          : Divider(
              height: height,
              thickness: thickness,
              indent: indent,
              endIndent: endIndent,
              color: defaultColor,
            );
    }

    return Padding(
      padding: padding ?? EdgeInsets.symmetric(vertical: height / 2),
      child: Row(
        children: [
          if (alignment != MainAxisAlignment.start)
            Expanded(
              child: Divider(
                thickness: thickness,
                indent: indent,
                color: defaultColor,
              ),
            ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Text(
              text!,
              style: textStyle ??
                  theme.textTheme.bodySmall?.copyWith(
                    color: theme.disabledColor,
                  ),
            ),
          ),
          if (alignment != MainAxisAlignment.end)
            Expanded(
              child: Divider(
                thickness: thickness,
                endIndent: endIndent,
                color: defaultColor,
              ),
            ),
        ],
      ),
    );
  }
} 