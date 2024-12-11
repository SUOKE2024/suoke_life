/// 滑块选择器组件
class SliderSelector extends StatefulWidget {
  final double value;
  final double min;
  final double max;
  final int? divisions;
  final ValueChanged<double>? onChanged;
  final String? label;
  final Color? activeColor;
  final Color? inactiveColor;
  final Color? thumbColor;
  final double? thumbSize;
  final Widget? prefix;
  final Widget? suffix;
  final bool showValue;
  final String? valuePrefix;
  final String? valueSuffix;
  final TextStyle? valueStyle;
  final bool enabled;

  const SliderSelector({
    super.key,
    required this.value,
    this.min = 0.0,
    this.max = 1.0,
    this.divisions,
    this.onChanged,
    this.label,
    this.activeColor,
    this.inactiveColor,
    this.thumbColor,
    this.thumbSize,
    this.prefix,
    this.suffix,
    this.showValue = false,
    this.valuePrefix,
    this.valueSuffix,
    this.valueStyle,
    this.enabled = true,
  }) : assert(min <= max);

  @override
  State<SliderSelector> createState() => _SliderSelectorState();
}

class _SliderSelectorState extends State<SliderSelector> {
  late double _value;

  @override
  void initState() {
    super.initState();
    _value = widget.value.clamp(widget.min, widget.max);
  }

  @override
  void didUpdateWidget(SliderSelector oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.value != oldWidget.value) {
      _value = widget.value.clamp(widget.min, widget.max);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultActiveColor = widget.activeColor ?? theme.primaryColor;
    final defaultInactiveColor = widget.inactiveColor ?? theme.dividerColor;
    final defaultThumbColor = widget.thumbColor ?? defaultActiveColor;

    Widget slider = SliderTheme(
      data: SliderThemeData(
        activeTrackColor: defaultActiveColor,
        inactiveTrackColor: defaultInactiveColor,
        thumbColor: defaultThumbColor,
        overlayColor: defaultActiveColor.withOpacity(0.12),
        thumbShape: RoundSliderThumbShape(
          enabledThumbRadius: widget.thumbSize ?? 10.0,
        ),
        overlayShape: RoundSliderOverlayShape(
          overlayRadius: (widget.thumbSize ?? 10.0) * 2,
        ),
      ),
      child: Slider(
        value: _value,
        min: widget.min,
        max: widget.max,
        divisions: widget.divisions,
        onChanged: widget.enabled
            ? (value) {
                setState(() => _value = value);
                widget.onChanged?.call(value);
              }
            : null,
      ),
    );

    if (widget.prefix != null || widget.suffix != null) {
      slider = Row(
        children: [
          if (widget.prefix != null) ...[
            widget.prefix!,
            const SizedBox(width: 16),
          ],
          Expanded(child: slider),
          if (widget.suffix != null) ...[
            const SizedBox(width: 16),
            widget.suffix!,
          ],
        ],
      );
    }

    if (widget.label != null || widget.showValue) {
      final valueText = [
        if (widget.valuePrefix != null) widget.valuePrefix!,
        _value.toString(),
        if (widget.valueSuffix != null) widget.valueSuffix!,
      ].join();

      slider = Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          if (widget.label != null) ...[
            Text(
              widget.label!,
              style: theme.textTheme.bodyMedium,
            ),
            const SizedBox(height: 8),
          ],
          Row(
            children: [
              Expanded(child: slider),
              if (widget.showValue) ...[
                const SizedBox(width: 16),
                Text(
                  valueText,
                  style: widget.valueStyle ??
                      theme.textTheme.bodySmall?.copyWith(
                        color: widget.enabled
                            ? defaultActiveColor
                            : theme.disabledColor,
                      ),
                ),
              ],
            ],
          ),
        ],
      );
    }

    return slider;
  }
} 