/// 卡片组件
class AppCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets? padding;
  final Color? color;
  final double? elevation;
  final VoidCallback? onTap;
  final BorderRadius? borderRadius;
  final bool selected;
  final Widget? header;
  final Widget? footer;

  const AppCard({
    super.key,
    required this.child,
    this.padding,
    this.color,
    this.elevation,
    this.onTap,
    this.borderRadius,
    this.selected = false,
    this.header,
    this.footer,
  });

  @override
  Widget build(BuildContext context) {
    final content = Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (header != null) ...[
          Padding(
            padding: padding ?? AppStyles.padding,
            child: header!,
          ),
          const Divider(height: 1),
        ],
        Padding(
          padding: padding ?? AppStyles.padding,
          child: child,
        ),
        if (footer != null) ...[
          const Divider(height: 1),
          Padding(
            padding: padding ?? AppStyles.padding,
            child: footer!,
          ),
        ],
      ],
    );

    final card = Card(
      color: selected 
          ? Theme.of(context).colorScheme.primary.withOpacity(0.1)
          : color,
      elevation: elevation ?? AppStyles.elevation,
      shape: RoundedRectangleBorder(
        borderRadius: borderRadius ?? AppStyles.borderRadius,
      ),
      child: content,
    );

    if (onTap != null) {
      return InkWell(
        onTap: onTap,
        borderRadius: borderRadius ?? AppStyles.borderRadius,
        child: card,
      );
    }

    return card;
  }
} 