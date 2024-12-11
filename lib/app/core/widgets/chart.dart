/// 简单图表组件
class SimpleChart extends StatelessWidget {
  final List<ChartData> data;
  final String? title;
  final double? height;
  final Color? barColor;
  final Color? gridColor;
  final bool showLabels;
  final bool showValues;
  final bool showGrid;
  final int gridLines;
  final EdgeInsets? padding;
  final TextStyle? labelStyle;
  final TextStyle? valueStyle;

  const SimpleChart({
    super.key,
    required this.data,
    this.title,
    this.height = 200,
    this.barColor,
    this.gridColor,
    this.showLabels = true,
    this.showValues = true,
    this.showGrid = true,
    this.gridLines = 5,
    this.padding,
    this.labelStyle,
    this.valueStyle,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultBarColor = barColor ?? theme.primaryColor;
    final defaultGridColor = gridColor ?? theme.dividerColor;

    if (data.isEmpty) return const SizedBox();

    final maxValue = data.map((e) => e.value).reduce(max);
    final gridStep = maxValue / (gridLines - 1);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (title != null) ...[
          Text(
            title!,
            style: theme.textTheme.titleMedium,
          ),
          const SizedBox(height: 16),
        ],
        Container(
          height: height,
          padding: padding ?? const EdgeInsets.all(16),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              if (showValues)
                Column(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: List.generate(gridLines, (index) {
                    final value = (gridStep * (gridLines - 1 - index));
                    return Text(
                      value.toStringAsFixed(1),
                      style: valueStyle ?? theme.textTheme.bodySmall,
                    );
                  }),
                ),
              const SizedBox(width: 8),
              Expanded(
                child: Stack(
                  children: [
                    if (showGrid)
                      Column(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: List.generate(
                          gridLines,
                          (index) => Container(
                            height: 1,
                            color: defaultGridColor,
                          ),
                        ),
                      ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: data.map((item) {
                        final height = item.value / maxValue * 100;
                        return Expanded(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.end,
                            children: [
                              Container(
                                height: height * 1.5,
                                margin: const EdgeInsets.symmetric(horizontal: 4),
                                decoration: BoxDecoration(
                                  color: defaultBarColor,
                                  borderRadius: const BorderRadius.vertical(
                                    top: Radius.circular(4),
                                  ),
                                ),
                              ),
                              if (showLabels) ...[
                                const SizedBox(height: 8),
                                Text(
                                  item.label,
                                  style: labelStyle ?? theme.textTheme.bodySmall,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ],
                            ],
                          ),
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

/// 图表数据
class ChartData {
  final String label;
  final double value;

  const ChartData({
    required this.label,
    required this.value,
  });
} 