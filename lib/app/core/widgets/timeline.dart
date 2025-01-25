import 'package:flutter/material.dart';

/// 时间线组件
class AppTimeline extends StatelessWidget {
  final List<AppTimelineItem> items;
  final bool reverse;
  final ScrollController? controller;
  final EdgeInsets? padding;
  final Color? lineColor;
  final double lineWidth;
  final Color? indicatorColor;
  final double indicatorSize;
  final Widget Function(BuildContext, AppTimelineItem)? itemBuilder;
  
  const AppTimeline({
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

        Widget child = itemBuilder?.call(context, item) ?? Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (item.title != null)
              Text(
                item.title!,
                style: theme.textTheme.titleMedium,
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
          ],
        );

        return IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              SizedBox(
                width: indicatorSize * 2,
                child: Column(
                  children: [
                    if (!isFirst)
                      Expanded(
                        child: Container(
                          width: lineWidth,
                          color: defaultLineColor,
                        ),
                      ),
                    Container(
                      width: indicatorSize,
                      height: indicatorSize,
                      decoration: BoxDecoration(
                        color: defaultIndicatorColor,
                        shape: BoxShape.circle,
                      ),
                    ),
                    if (!isLast)
                      Expanded(
                        child: Container(
                          width: lineWidth,
                          color: defaultLineColor,
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              Expanded(child: child),
            ],
          ),
        );
      },
    );
  }
}

/// 时间线项
class AppTimelineItem {
  final String? title;
  final String? subtitle;
  final Widget? content;
  
  const AppTimelineItem({
    this.title,
    this.subtitle,
    this.content,
  });
} 