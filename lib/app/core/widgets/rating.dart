/// 评分组件
class Rating extends StatelessWidget {
  final double value;
  final int count;
  final double size;
  final Color? activeColor;
  final Color? inactiveColor;
  final ValueChanged<double>? onChanged;
  final bool allowHalfRating;
  final bool readOnly;
  final Widget? activeIcon;
  final Widget? inactiveIcon;
  final Widget? halfIcon;
  final MainAxisAlignment alignment;
  final double spacing;

  const Rating({
    super.key,
    required this.value,
    this.count = 5,
    this.size = 24,
    this.activeColor,
    this.inactiveColor,
    this.onChanged,
    this.allowHalfRating = true,
    this.readOnly = false,
    this.activeIcon,
    this.inactiveIcon,
    this.halfIcon,
    this.alignment = MainAxisAlignment.start,
    this.spacing = 4,
  }) : assert(value >= 0 && value <= count);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultActiveColor = activeColor ?? theme.primaryColor;
    final defaultInactiveColor = inactiveColor ?? theme.disabledColor;

    Widget buildIcon(int index) {
      final active = value >= index + 1;
      final half = allowHalfRating && value > index && value < index + 1;

      Widget icon;
      if (active) {
        icon = activeIcon ??
            Icon(
              Icons.star,
              size: size,
              color: defaultActiveColor,
            );
      } else if (half) {
        icon = halfIcon ??
            Icon(
              Icons.star_half,
              size: size,
              color: defaultActiveColor,
            );
      } else {
        icon = inactiveIcon ??
            Icon(
              Icons.star_border,
              size: size,
              color: defaultInactiveColor,
            );
      }

      if (readOnly) return icon;

      return GestureDetector(
        onTapDown: (details) {
          final box = context.findRenderObject() as RenderBox;
          final localPosition = box.globalToLocal(details.globalPosition);
          final rating = _calculateRating(index, localPosition.dx, box.size.width);
          onChanged?.call(rating);
        },
        child: icon,
      );
    }

    return Row(
      mainAxisAlignment: alignment,
      mainAxisSize: MainAxisSize.min,
      children: List.generate(
        count * 2 - 1,
        (index) {
          if (index.isOdd) return SizedBox(width: spacing);
          return buildIcon(index ~/ 2);
        },
      ),
    );
  }

  double _calculateRating(int index, double dx, double width) {
    final itemWidth = (width - spacing * (count - 1)) / count;
    final itemIndex = index * (itemWidth + spacing);
    final position = dx - itemIndex;

    if (allowHalfRating) {
      if (position < itemWidth / 2) {
        return index + 0.5;
      }
    }
    return index + 1.0;
  }
} 