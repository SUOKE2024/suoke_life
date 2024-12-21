import 'package:flutter/material.dart';

/// 滑块组件
class AppSlider extends StatelessWidget {
  final double value;
  final ValueChanged<double>? onChanged;
  final ValueChanged<double>? onChangeStart;
  final ValueChanged<double>? onChangeEnd;
  final double min;
  final double max;
  final int? divisions;
  final String? label;
  final Color? activeColor;
  final Color? inactiveColor;
  final Color? thumbColor;
  final double thumbSize;
  final bool enabled;
  
  const AppSlider({
    super.key,
    required this.value,
    this.onChanged,
    this.onChangeStart,
    this.onChangeEnd,
    this.min = 0.0,
    this.max = 1.0,
    this.divisions,
    this.label,
    this.activeColor,
    this.inactiveColor,
    this.thumbColor,
    this.thumbSize = 20,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return SliderTheme(
      data: SliderThemeData(
        activeTrackColor: activeColor ?? theme.primaryColor,
        inactiveTrackColor: inactiveColor ?? theme.disabledColor.withOpacity(0.3),
        thumbColor: thumbColor ?? theme.primaryColor,
        overlayColor: theme.primaryColor.withOpacity(0.1),
        thumbShape: RoundSliderThumbShape(
          enabledThumbRadius: thumbSize / 2,
          disabledThumbRadius: thumbSize / 2,
        ),
        overlayShape: RoundSliderOverlayShape(
          overlayRadius: thumbSize,
        ),
      ),
      child: Slider(
        value: value,
        onChanged: enabled ? onChanged : null,
        onChangeStart: enabled ? onChangeStart : null,
        onChangeEnd: enabled ? onChangeEnd : null,
        min: min,
        max: max,
        divisions: divisions,
        label: label,
      ),
    );
  }
} 