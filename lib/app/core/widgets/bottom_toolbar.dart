/// 底部工具栏组件
class BottomToolbar extends StatelessWidget {
  final List<Widget> children;
  final Color? backgroundColor;
  final double height;
  final EdgeInsets? padding;
  final bool showDivider;
  final bool safeArea;
  final double? elevation;

  const BottomToolbar({
    super.key,
    required this.children,
    this.backgroundColor,
    this.height = 56,
    this.padding,
    this.showDivider = true,
    this.safeArea = true,
    this.elevation,
  });

  @override
  Widget build(BuildContext context) {
    Widget toolbar = Material(
      elevation: elevation ?? 4,
      color: backgroundColor ?? Theme.of(context).scaffoldBackgroundColor,
      child: Container(
        height: height,
        padding: padding ?? AppStyles.padding,
        decoration: showDivider ? BoxDecoration(
          border: Border(
            top: BorderSide(
              color: Theme.of(context).dividerColor,
            ),
          ),
        ) : null,
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: children,
        ),
      ),
    );

    if (safeArea) {
      toolbar = SafeArea(child: toolbar);
    }

    return toolbar;
  }
} 