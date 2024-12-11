/// 评分组件
class AppRatingBar extends StatelessWidget {
  final double rating;
  final ValueChanged<double>? onRatingChanged;
  final int itemCount;
  final double itemSize;
  final Color? selectedColor;
  final Color? unselectedColor;
  final IconData selectedIcon;
  final IconData unselectedIcon;
  final bool allowHalfRating;
  final bool ignoreGestures;
  final String? label;

  const AppRatingBar({
    super.key,
    required this.rating,
    this.onRatingChanged,
    this.itemCount = 5,
    this.itemSize = 24,
    this.selectedColor,
    this.unselectedColor,
    this.selectedIcon = Icons.star,
    this.unselectedIcon = Icons.star_border,
    this.allowHalfRating = true,
    this.ignoreGestures = false,
    this.label,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (label != null) ...[
          Text(
            label!,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 8),
        ],
        Row(
          mainAxisSize: MainAxisSize.min,
          children: List.generate(itemCount, (index) {
            final value = index + 1;
            final isSelected = value <= rating;
            final isHalf = allowHalfRating && value > rating && value - 0.5 <= rating;

            return GestureDetector(
              onTapDown: ignoreGestures
                  ? null
                  : (details) {
                      final box = context.findRenderObject() as RenderBox;
                      final localPosition = box.globalToLocal(details.globalPosition);
                      final percent = localPosition.dx / (itemSize * itemCount);
                      final newRating = (percent * itemCount).clamp(0.0, itemCount.toDouble());
                      onRatingChanged?.call(
                        allowHalfRating ? (newRating * 2).round() / 2 : newRating.round().toDouble(),
                      );
                    },
              child: Icon(
                isHalf ? Icons.star_half : (isSelected ? selectedIcon : unselectedIcon),
                size: itemSize,
                color: isSelected || isHalf
                    ? selectedColor ?? Theme.of(context).primaryColor
                    : unselectedColor ?? Theme.of(context).disabledColor,
              ),
            );
          }),
        ),
      ],
    );
  }
} 