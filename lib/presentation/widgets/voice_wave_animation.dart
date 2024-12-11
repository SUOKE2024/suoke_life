import 'dart:math';
import 'package:flutter/material.dart';

class VoiceWaveAnimation extends StatefulWidget {
  const VoiceWaveAnimation({Key? key}) : super(key: key);

  @override
  _VoiceWaveAnimationState createState() => _VoiceWaveAnimationState();
}

class _VoiceWaveAnimationState extends State<VoiceWaveAnimation>
    with TickerProviderStateMixin {
  late List<AnimationController> _controllers;
  late List<Animation<double>> _animations;
  final int _barsCount = 5;
  final Random _random = Random();

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
  }

  void _initializeAnimations() {
    _controllers = List.generate(
      _barsCount,
      (index) => AnimationController(
        duration: Duration(milliseconds: 300 + _random.nextInt(700)),
        vsync: this,
      ),
    );

    _animations = _controllers.map((controller) {
      return Tween<double>(begin: 0.1, end: 1.0).animate(
        CurvedAnimation(
          parent: controller,
          curve: Curves.easeInOut,
        ),
      );
    }).toList();

    for (var controller in _controllers) {
      controller.repeat(reverse: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(
        _barsCount,
        (index) => _buildBar(index),
      ),
    );
  }

  Widget _buildBar(int index) {
    return AnimatedBuilder(
      animation: _animations[index],
      builder: (context, child) {
        return Container(
          margin: const EdgeInsets.symmetric(horizontal: 2),
          width: 4,
          height: 32 * _animations[index].value,
          decoration: BoxDecoration(
            color: Theme.of(context).primaryColor.withOpacity(0.7),
            borderRadius: BorderRadius.circular(2),
          ),
        );
      },
    );
  }

  @override
  void dispose() {
    for (var controller in _controllers) {
      controller.dispose();
    }
    super.dispose();
  }
} 