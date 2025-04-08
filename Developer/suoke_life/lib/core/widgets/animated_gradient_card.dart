import 'package:flutter/material.dart';
import '../theme/colors.dart';

class AnimatedGradientCard extends StatefulWidget {
  final String title;
  final String subtitle;
  final Widget child;
  final List<Color> gradientColors;
  final EdgeInsetsGeometry padding;
  final double borderRadius;
  final VoidCallback? onTap;

  const AnimatedGradientCard({
    Key? key,
    required this.title,
    required this.subtitle,
    required this.child,
    this.gradientColors = const [AppColors.primaryColor, AppColors.primaryDarkColor],
    this.padding = const EdgeInsets.all(16.0),
    this.borderRadius = 16.0,
    this.onTap,
  }) : super(key: key);

  @override
  State<AnimatedGradientCard> createState() => _AnimatedGradientCardState();
}

class _AnimatedGradientCardState extends State<AnimatedGradientCard> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(seconds: 5),
      vsync: this,
    )..repeat(reverse: true);
    
    _animation = Tween<double>(begin: -0.5, end: 1.5).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeInOut,
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: widget.onTap,
      child: AnimatedBuilder(
        animation: _animation,
        builder: (context, child) {
          return Container(
            padding: widget.padding,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(widget.borderRadius),
              gradient: LinearGradient(
                colors: widget.gradientColors,
                begin: Alignment(_animation.value, 0),
                end: Alignment(_animation.value + 1, 1),
              ),
              boxShadow: [
                BoxShadow(
                  color: widget.gradientColors.first.withAlpha(60),
                  blurRadius: 12,
                  offset: const Offset(0, 6),
                ),
              ],
            ),
            child: child,
          );
        },
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.title,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              widget.subtitle,
              style: TextStyle(
                color: Colors.white.withAlpha(200),
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 16),
            widget.child,
          ],
        ),
      ),
    );
  }
} 