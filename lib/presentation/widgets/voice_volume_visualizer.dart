import 'package:flutter/material.dart';
import 'dart:math' as math;

class VoiceVolumeVisualizer extends StatefulWidget {
  final double volume;
  final Color color;
  final double height;

  const VoiceVolumeVisualizer({
    super.key,
    required this.volume,
    this.color = Colors.blue,
    this.height = 100,
  });

  @override
  State<VoiceVolumeVisualizer> createState() => _VoiceVolumeVisualizerState();
}

class _VoiceVolumeVisualizerState extends State<VoiceVolumeVisualizer>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  final List<double> _volumeHistory = List.filled(30, 0.0);
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 50),
    )..addListener(_updateVolume);
    _controller.repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _updateVolume() {
    setState(() {
      _volumeHistory[_currentIndex] = widget.volume;
      _currentIndex = (_currentIndex + 1) % _volumeHistory.length;
    });
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: widget.height,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: List.generate(_volumeHistory.length, (index) {
          final normalizedIndex = (index + _currentIndex) % _volumeHistory.length;
          final volume = _volumeHistory[normalizedIndex];
          
          // 添加一些随机波动使动画更自然
          final random = math.Random();
          final randomFactor = 1.0 + (random.nextDouble() - 0.5) * 0.2;
          final height = (volume * widget.height * 0.8 * randomFactor)
              .clamp(widget.height * 0.1, widget.height * 0.8);

          return AnimatedContainer(
            duration: const Duration(milliseconds: 50),
            width: 4,
            height: height,
            decoration: BoxDecoration(
              color: widget.color.withOpacity(0.8),
              borderRadius: BorderRadius.circular(2),
            ),
          );
        }),
      ),
    );
  }
} 