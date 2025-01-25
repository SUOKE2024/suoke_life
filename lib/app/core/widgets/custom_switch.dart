import 'package:flutter/material.dart';

class CustomSwitch extends StatelessWidget {
  final bool value;
  final ValueChanged<bool>? onChanged;
  final Color? activeColor;
  final Color? inactiveColor;

  const CustomSwitch({
    Key? key,
    required this.value,
    this.onChanged,
    this.activeColor,
    this.inactiveColor,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Switch(
      value: value,
      onChanged: onChanged,
      activeColor: activeColor ?? Theme.of(context).primaryColor,
      inactiveThumbColor: inactiveColor ?? Colors.grey[300],
      activeTrackColor: activeColor?.withOpacity(0.5) ?? Theme.of(context).primaryColor.withOpacity(0.5),
      inactiveTrackColor: inactiveColor?.withOpacity(0.5) ?? Colors.grey[300]?.withOpacity(0.5),
    );
  }
} 