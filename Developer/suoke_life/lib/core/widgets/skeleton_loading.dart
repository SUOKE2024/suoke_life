import 'package:flutter/material.dart';

/// 骨架屏加载组件
/// 用于在数据加载期间显示占位UI
class SkeletonLoading extends StatefulWidget {
  final double width;
  final double height;
  final BorderRadius? borderRadius;
  final Color? baseColor;
  final Color? highlightColor;
  final bool isCircle;

  const SkeletonLoading({
    Key? key,
    this.width = double.infinity,
    this.height = 12.0,
    this.borderRadius,
    this.baseColor,
    this.highlightColor,
    this.isCircle = false,
  }) : super(key: key);

  @override
  _SkeletonLoadingState createState() => _SkeletonLoadingState();
}

class _SkeletonLoadingState extends State<SkeletonLoading>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat();

    _animation = Tween<double>(begin: -2.0, end: 2.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOutSine),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final baseColor = widget.baseColor ?? Theme.of(context).colorScheme.surfaceVariant;
    final highlightColor = widget.highlightColor ?? Theme.of(context).colorScheme.surface;
    
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            shape: widget.isCircle ? BoxShape.circle : BoxShape.rectangle,
            borderRadius: widget.isCircle ? null : (widget.borderRadius ?? BorderRadius.circular(4)),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [baseColor, highlightColor, baseColor],
              stops: [
                0.0,
                (_animation.value + 2) / 4,
                1.0,
              ],
            ),
          ),
        );
      },
    );
  }
}

/// 骨架消息条目
/// 用于在消息加载期间显示占位UI
class SkeletonMessageItem extends StatelessWidget {
  final bool isUserMessage;
  final double width;
  
  const SkeletonMessageItem({
    Key? key,
    this.isUserMessage = false,
    this.width = 200,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
      child: Row(
        mainAxisAlignment: isUserMessage ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          if (!isUserMessage) 
            Padding(
              padding: const EdgeInsets.only(right: 8.0),
              child: SkeletonLoading(
                width: 36,
                height: 36,
                isCircle: true,
              ),
            ),
          Column(
            crossAxisAlignment: isUserMessage ? CrossAxisAlignment.end : CrossAxisAlignment.start,
            children: [
              SkeletonLoading(
                width: width,
                height: 12,
                borderRadius: BorderRadius.circular(4),
              ),
              const SizedBox(height: 4),
              SkeletonLoading(
                width: width * 0.7,
                height: 12,
                borderRadius: BorderRadius.circular(4),
              ),
              const SizedBox(height: 4),
              SkeletonLoading(
                width: width * 0.5,
                height: 12,
                borderRadius: BorderRadius.circular(4),
              ),
            ],
          ),
          if (isUserMessage) 
            Padding(
              padding: const EdgeInsets.only(left: 8.0),
              child: SkeletonLoading(
                width: 36,
                height: 36,
                isCircle: true,
              ),
            ),
        ],
      ),
    );
  }
} 