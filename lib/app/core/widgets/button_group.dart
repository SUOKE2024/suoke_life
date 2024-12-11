/// 按钮组组件
class ButtonGroup extends StatelessWidget {
  final List<ButtonItem> items;
  final ValueChanged<int>? onSelected;
  final int? selectedIndex;
  final ButtonGroupStyle style;
  final double? spacing;
  final double? height;
  final bool isScrollable;
  final EdgeInsets? padding;
  final BorderRadius? borderRadius;
  final Color? selectedColor;
  final Color? unselectedColor;
  final TextStyle? selectedTextStyle;
  final TextStyle? unselectedTextStyle;

  const ButtonGroup({
    super.key,
    required this.items,
    this.onSelected,
    this.selectedIndex,
    this.style = ButtonGroupStyle.outlined,
    this.spacing,
    this.height,
    this.isScrollable = false,
    this.padding,
    this.borderRadius,
    this.selectedColor,
    this.unselectedColor,
    this.selectedTextStyle,
    this.unselectedTextStyle,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultSelectedColor = selectedColor ?? theme.primaryColor;
    final defaultUnselectedColor = unselectedColor ?? theme.dividerColor;
    final defaultSpacing = spacing ?? 1.0;

    Widget buildButton(int index) {
      final item = items[index];
      final selected = selectedIndex == index;
      final defaultHeight = height ?? 36.0;

      Widget button;
      switch (style) {
        case ButtonGroupStyle.outlined:
          button = OutlinedButton(
            onPressed: item.onPressed ?? () => onSelected?.call(index),
            style: OutlinedButton.styleFrom(
              foregroundColor: selected ? defaultSelectedColor : defaultUnselectedColor,
              side: BorderSide(
                color: selected ? defaultSelectedColor : defaultUnselectedColor,
              ),
              padding: padding ?? const EdgeInsets.symmetric(horizontal: 16),
              minimumSize: Size(0, defaultHeight),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.zero,
              ),
            ),
            child: item.child,
          );
          break;
        case ButtonGroupStyle.filled:
          button = ElevatedButton(
            onPressed: item.onPressed ?? () => onSelected?.call(index),
            style: ElevatedButton.styleFrom(
              foregroundColor: selected ? Colors.white : defaultUnselectedColor,
              backgroundColor: selected ? defaultSelectedColor : Colors.transparent,
              padding: padding ?? const EdgeInsets.symmetric(horizontal: 16),
              minimumSize: Size(0, defaultHeight),
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.zero,
              ),
            ),
            child: item.child,
          );
          break;
        case ButtonGroupStyle.text:
          button = TextButton(
            onPressed: item.onPressed ?? () => onSelected?.call(index),
            style: TextButton.styleFrom(
              foregroundColor: selected ? defaultSelectedColor : defaultUnselectedColor,
              padding: padding ?? const EdgeInsets.symmetric(horizontal: 16),
              minimumSize: Size(0, defaultHeight),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.zero,
              ),
            ),
            child: item.child,
          );
          break;
      }

      // 添加分隔线
      if (index > 0 && style != ButtonGroupStyle.text) {
        button = Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              height: defaultHeight,
              child: VerticalDivider(
                width: defaultSpacing,
                thickness: defaultSpacing,
                color: defaultUnselectedColor,
              ),
            ),
            button,
          ],
        );
      }

      return button;
    }

    final buttonList = List.generate(
      items.length,
      (index) => buildButton(index),
    );

    Widget group = isScrollable
        ? SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: buttonList,
            ),
          )
        : Row(
            children: buttonList.map((button) => Expanded(child: button)).toList(),
          );

    // 添加圆角边框
    if (borderRadius != null) {
      group = ClipRRect(
        borderRadius: borderRadius!,
        child: group,
      );
    }

    // 添加边框
    if (style != ButtonGroupStyle.text) {
      group = DecoratedBox(
        decoration: BoxDecoration(
          border: Border.all(
            color: defaultUnselectedColor,
            width: defaultSpacing,
          ),
          borderRadius: borderRadius,
        ),
        child: group,
      );
    }

    return group;
  }
}

/// 按钮组样式
enum ButtonGroupStyle {
  outlined,
  filled,
  text,
}

/// 按钮项
class ButtonItem {
  final Widget child;
  final VoidCallback? onPressed;

  const ButtonItem({
    required this.child,
    this.onPressed,
  });
} 