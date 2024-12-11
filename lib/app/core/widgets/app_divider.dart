/// 分割线组件
class AppDivider extends StatelessWidget {
  final double height;
  final double thickness;
  final double indent;
  final double endIndent;
  final Color? color;
  final bool vertical;

  const AppDivider({
    super.key,
    this.height = 1,
    this.thickness = 1,
    this.indent = 0,
    this.endIndent = 0,
    this.color,
    this.vertical = false,
  });

  @override
  Widget build(BuildContext context) {
    if (vertical) {
      return VerticalDivider(
        width: height,
        thickness: thickness,
        indent: indent,
        endIndent: endIndent,
        color: color ?? Theme.of(context).dividerColor,
      );
    }

    return Divider(
      height: height,
      thickness: thickness,
      indent: indent,
      endIndent: endIndent,
      color: color ?? Theme.of(context).dividerColor,
    );
  }

  /// 带文本的分割线
  static Widget withText(
    String text, {
    TextStyle? style,
    Color? color,
    double spacing = 16,
  }) {
    return Builder(
      builder: (context) {
        return Row(
          children: [
            Expanded(
              child: AppDivider(color: color),
            ),
            Padding(
              padding: EdgeInsets.symmetric(horizontal: spacing),
              child: Text(
                text,
                style: style ?? Theme.of(context).textTheme.bodySmall,
              ),
            ),
            Expanded(
              child: AppDivider(color: color),
            ),
          ],
        );
      },
    );
  }
} 