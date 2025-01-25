/// 颜色选择器组件
class AppColorPicker extends StatelessWidget {
  final Color? value;
  final ValueChanged<Color>? onChanged;
  final List<Color>? colors;
  final double size;
  final double spacing;
  final bool showLabel;
  final bool enableAlpha;
  final bool enableCustom;
  final String? label;
  final String? hint;
  final String? customText;
  final String? cancelText;
  final String? confirmText;

  const AppColorPicker({
    super.key,
    this.value,
    this.onChanged,
    this.colors,
    this.size = 40,
    this.spacing = 8,
    this.showLabel = true,
    this.enableAlpha = false,
    this.enableCustom = true,
    this.label,
    this.hint,
    this.customText,
    this.cancelText,
    this.confirmText,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultColors = colors ??
        [
          Colors.red,
          Colors.pink,
          Colors.purple,
          Colors.deepPurple,
          Colors.indigo,
          Colors.blue,
          Colors.lightBlue,
          Colors.cyan,
          Colors.teal,
          Colors.green,
          Colors.lightGreen,
          Colors.lime,
          Colors.yellow,
          Colors.amber,
          Colors.orange,
          Colors.deepOrange,
          Colors.brown,
          Colors.grey,
          Colors.blueGrey,
          Colors.black,
        ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (label != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(
              label!,
              style: theme.textTheme.bodyMedium,
            ),
          ),
        Wrap(
          spacing: spacing,
          runSpacing: spacing,
          children: [
            ...defaultColors.map((color) {
              final selected = value?.value == color.value;
              return _ColorItem(
                color: color,
                size: size,
                selected: selected,
                onTap: () => onChanged?.call(color),
              );
            }),
            if (enableCustom)
              _ColorItem(
                color: Colors.transparent,
                size: size,
                selected: false,
                child: Icon(
                  Icons.add,
                  size: size * 0.6,
                  color: theme.iconTheme.color,
                ),
                onTap: () => _showCustomColorPicker(context),
              ),
          ],
        ),
      ],
    );
  }

  Future<void> _showCustomColorPicker(BuildContext context) async {
    final result = await showDialog<Color>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(customText ?? '自定义颜色'),
        content: SingleChildScrollView(
          child: ColorPicker(
            pickerColor: value ?? Colors.blue,
            onColorChanged: (color) {},
            enableAlpha: enableAlpha,
            labelTypes: showLabel ? null : const [],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(cancelText ?? '取消'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(value),
            child: Text(confirmText ?? '确定'),
          ),
        ],
      ),
    );

    if (result != null) {
      onChanged?.call(result);
    }
  }
}

class _ColorItem extends StatelessWidget {
  final Color color;
  final double size;
  final bool selected;
  final Widget? child;
  final VoidCallback? onTap;

  const _ColorItem({
    required this.color,
    required this.size,
    required this.selected,
    this.child,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(size / 2),
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          color: color,
          border: Border.all(
            color: selected ? Theme.of(context).primaryColor : Colors.grey[300]!,
            width: selected ? 2 : 1,
          ),
          borderRadius: BorderRadius.circular(size / 2),
        ),
        child: child,
      ),
    );
  }
} 