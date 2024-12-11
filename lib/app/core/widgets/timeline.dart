/// 时间轴组件
class Timeline extends StatelessWidget {
  final List<TimelineItem> items;
  final bool reverse;
  final ScrollController? controller;
  final EdgeInsets? padding;
  final Color? lineColor;
  final double lineWidth;
  final Color? indicatorColor;
  final double indicatorSize;
  final Widget Function(BuildContext, TimelineItem)? itemBuilder;

  const Timeline({
    super.key,
    required this.items,
    this.reverse = false,
    this.controller,
    this.padding,
    this.lineColor,
    this.lineWidth = 2,
    this.indicatorColor,
    this.indicatorSize = 12,
    this.itemBuilder,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultLineColor = lineColor ?? theme.dividerColor;
    final defaultIndicatorColor = indicatorColor ?? theme.primaryColor;

    return ListView.builder(
      controller: controller,
      padding: padding,
      reverse: reverse,
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        final isFirst = index == 0;
        final isLast = index == items.length - 1;

        if (itemBuilder != null) {
          return itemBuilder!(context, item);
        }

        return IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              SizedBox(
                width: 32,
                child: Column(
                  children: [
                    if (!isFirst)
                      Expanded(
                        flex: 1,
                        child: Container(
                          width: lineWidth,
                          color: defaultLineColor,
                        ),
                      ),
                    Container(
                      width: indicatorSize,
                      height: indicatorSize,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: defaultIndicatorColor,
                      ),
                    ),
                    if (!isLast)
                      Expanded(
                        flex: 3,
                        child: Container(
                          width: lineWidth,
                          color: defaultLineColor,
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          item.title,
                          style: theme.textTheme.titleMedium,
                        ),
                        const Spacer(),
                        if (item.time != null)
                          Text(
                            item.time!,
                            style: theme.textTheme.bodySmall,
                          ),
                      ],
                    ),
                    if (item.subtitle != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        item.subtitle!,
                        style: theme.textTheme.bodySmall,
                      ),
                    ],
                    if (item.content != null) ...[
                      const SizedBox(height: 8),
                      item.content!,
                    ],
                    const SizedBox(height: 16),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

/// 时间轴项
class TimelineItem {
  final String title;
  final String? subtitle;
  final String? time;
  final Widget? content;

  const TimelineItem({
    required this.title,
    this.subtitle,
    this.time,
    this.content,
  });
} 