import 'package:flutter/material.dart';

/// 开关组件
class AppSwitch extends StatelessWidget {
  final bool value;
  final ValueChanged<bool>? onChanged;
  final Color? activeColor;
  final Color? activeTrackColor;
  final Color? inactiveThumbColor;
  final Color? inactiveTrackColor;
  final ImageProvider? activeThumbImage;
  final ImageProvider? inactiveThumbImage;
  final MaterialStateProperty<Color?>? thumbColor;
  final MaterialStateProperty<Color?>? trackColor;
  final MaterialStateProperty<Color?>? overlayColor;
  final double? splashRadius;
  final MaterialTapTargetSize? materialTapTargetSize;
  final DragStartBehavior dragStartBehavior;
  final bool autofocus;
  final bool enabled;
  
  const AppSwitch({
    super.key,
    required this.value,
    required this.onChanged,
    this.activeColor,
    this.activeTrackColor,
    this.inactiveThumbColor,
    this.inactiveTrackColor,
    this.activeThumbImage,
    this.inactiveThumbImage,
    this.thumbColor,
    this.trackColor,
    this.overlayColor,
    this.splashRadius,
    this.materialTapTargetSize,
    this.dragStartBehavior = DragStartBehavior.start,
    this.autofocus = false,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    return Switch(
      value: value,
      onChanged: enabled ? onChanged : null,
      activeColor: activeColor,
      activeTrackColor: activeTrackColor,
      inactiveThumbColor: inactiveThumbColor,
      inactiveTrackColor: inactiveTrackColor,
      activeThumbImage: activeThumbImage,
      inactiveThumbImage: inactiveThumbImage,
      thumbColor: thumbColor,
      trackColor: trackColor,
      overlayColor: overlayColor,
      splashRadius: splashRadius,
      materialTapTargetSize: materialTapTargetSize,
      dragStartBehavior: dragStartBehavior,
      autofocus: autofocus,
    );
  }
} 