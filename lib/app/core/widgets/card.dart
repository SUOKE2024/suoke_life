import 'package:flutter/material.dart';

/// 卡片组件
class AppCard extends StatelessWidget {
  final Widget child;
  final Color? color;
  final Color? shadowColor;
  final double? elevation;
  final EdgeInsets? margin;
  final EdgeInsets? padding;
  final ShapeBorder? shape;
  final BorderRadius? borderRadius;
  final Clip? clipBehavior;
  final bool semanticContainer;
  final VoidCallback? onTap;
  
  const AppCard({
    super.key,
    required this.child,
    this.color,
    this.shadowColor,
    this.elevation,
    this.margin,
    this.padding,
    this.shape,
    this.borderRadius,
    this.clipBehavior,
    this.semanticContainer = true,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    Widget card = Card(
      color: color,
      shadowColor: shadowColor,
      elevation: elevation,
      margin: margin,
      shape: shape ?? (borderRadius != null
          ? RoundedRectangleBorder(
              borderRadius: borderRadius!,
            )
          : null),
      clipBehavior: clipBehavior,
      semanticContainer: semanticContainer,
      child: Padding(
        padding: padding ?? EdgeInsets.zero,
        child: child,
      ),
    );

    if (onTap != null) {
      card = InkWell(
        onTap: onTap,
        borderRadius: borderRadius,
        child: card,
      );
    }

    return card;
  }
}

/// 可展开卡片组件
class AppExpandableCard extends StatefulWidget {
  final Widget title;
  final Widget child;
  final bool initiallyExpanded;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final Color? color;
  final double? elevation;
  final ShapeBorder? shape;
  final BorderRadius? borderRadius;
  
  const AppExpandableCard({
    super.key,
    required this.title,
    required this.child,
    this.initiallyExpanded = false,
    this.padding,
    this.margin,
    this.color,
    this.elevation,
    this.shape,
    this.borderRadius,
  });

  @override
  State<AppExpandableCard> createState() => _AppExpandableCardState();
}

class _AppExpandableCardState extends State<AppExpandableCard> {
  late bool _expanded;

  @override
  void initState() {
    super.initState();
    _expanded = widget.initiallyExpanded;
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: widget.margin ?? const EdgeInsets.all(8),
      color: widget.color,
      elevation: widget.elevation,
      shape: widget.shape ?? RoundedRectangleBorder(
        borderRadius: widget.borderRadius ?? BorderRadius.circular(8),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          InkWell(
            onTap: () => setState(() => _expanded = !_expanded),
            child: Padding(
              padding: widget.padding ?? const EdgeInsets.all(16),
              child: Row(
                children: [
                  Expanded(child: widget.title),
                  Icon(
                    _expanded ? Icons.expand_less : Icons.expand_more,
                  ),
                ],
              ),
            ),
          ),
          if (_expanded)
            Padding(
              padding: widget.padding ?? const EdgeInsets.all(16),
              child: widget.child,
            ),
        ],
      ),
    );
  }
} 