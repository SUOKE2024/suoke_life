/// 卡片组件
class AppCard extends StatelessWidget {
  final String? title;
  final String? subtitle;
  final Widget? leading;
  final Widget? trailing;
  final Widget? child;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final Color? color;
  final double? elevation;
  final BorderRadius? borderRadius;
  final VoidCallback? onTap;
  final bool showDivider;

  const AppCard({
    super.key,
    this.title,
    this.subtitle,
    this.leading,
    this.trailing,
    this.child,
    this.padding,
    this.margin,
    this.color,
    this.elevation,
    this.borderRadius,
    this.onTap,
    this.showDivider = true,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    Widget? header;
    if (title != null || subtitle != null || leading != null || trailing != null) {
      header = ListTile(
        leading: leading,
        title: title != null ? Text(title!) : null,
        subtitle: subtitle != null ? Text(subtitle!) : null,
        trailing: trailing,
      );
    }

    return Card(
      margin: margin ?? const EdgeInsets.all(8),
      color: color,
      elevation: elevation,
      shape: RoundedRectangleBorder(
        borderRadius: borderRadius ?? BorderRadius.circular(8),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: borderRadius ?? BorderRadius.circular(8),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (header != null) header,
            if (header != null && showDivider && child != null)
              const Divider(height: 1),
            if (child != null)
              Padding(
                padding: padding ?? const EdgeInsets.all(16),
                child: child,
              ),
          ],
        ),
      ),
    );
  }
} 