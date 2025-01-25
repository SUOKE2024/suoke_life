/// 列表项组件
class ListItem extends StatelessWidget {
  final Widget? leading;
  final Widget title;
  final Widget? subtitle;
  final Widget? trailing;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final bool selected;
  final EdgeInsets? padding;
  final double? height;

  const ListItem({
    super.key,
    this.leading,
    required this.title,
    this.subtitle,
    this.trailing,
    this.onTap,
    this.onLongPress,
    this.selected = false,
    this.padding,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: selected 
        ? Theme.of(context).colorScheme.primary.withOpacity(0.1)
        : null,
      child: InkWell(
        onTap: onTap,
        onLongPress: onLongPress,
        child: Container(
          height: height,
          padding: padding ?? AppStyles.padding,
          child: Row(
            children: [
              if (leading != null) ...[
                leading!,
                const SizedBox(width: 16),
              ],
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    DefaultTextStyle(
                      style: Theme.of(context).textTheme.bodyLarge!,
                      child: title,
                    ),
                    if (subtitle != null) ...[
                      const SizedBox(height: 4),
                      DefaultTextStyle(
                        style: Theme.of(context).textTheme.bodyMedium!,
                        child: subtitle!,
                      ),
                    ],
                  ],
                ),
              ),
              if (trailing != null) ...[
                const SizedBox(width: 16),
                trailing!,
              ],
            ],
          ),
        ),
      ),
    );
  }
} 