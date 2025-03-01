import 'package:flutter/material.dart';

class ServiceSection extends StatelessWidget {
  final String title;
  final String? subtitle;
  final List<Widget> children;
  final bool isScrollable;
  final VoidCallback? onViewMore;
  final EdgeInsetsGeometry padding;
  final double spacing;
  final double runSpacing;
  
  const ServiceSection({
    Key? key,
    required this.title,
    this.subtitle,
    required this.children,
    this.isScrollable = true,
    this.onViewMore,
    this.padding = const EdgeInsets.all(16),
    this.spacing = 12,
    this.runSpacing = 16,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: padding,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionHeader(context),
          const SizedBox(height: 16),
          if (isScrollable)
            _buildHorizontalList()
          else
            _buildWrappedGrid(),
        ],
      ),
    );
  }
  
  Widget _buildSectionHeader(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (subtitle != null)
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(
                    subtitle!,
                    style: TextStyle(
                      fontSize: 14,
                      color: Theme.of(context).textTheme.bodySmall?.color,
                    ),
                  ),
                ),
            ],
          ),
        ),
        if (onViewMore != null)
          TextButton(
            onPressed: onViewMore,
            child: Row(
              children: [
                const Text('查看更多'),
                const SizedBox(width: 4),
                Icon(
                  Icons.arrow_forward,
                  size: 16,
                  color: Theme.of(context).primaryColor,
                ),
              ],
            ),
          ),
      ],
    );
  }
  
  Widget _buildHorizontalList() {
    return SizedBox(
      height: 200, // 根据卡片高度调整
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: children.length,
        itemBuilder: (context, index) => children[index],
        separatorBuilder: (context, index) => SizedBox(width: spacing),
      ),
    );
  }
  
  Widget _buildWrappedGrid() {
    return Wrap(
      spacing: spacing,
      runSpacing: runSpacing,
      children: children,
    );
  }
} 