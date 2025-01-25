import 'package:flutter/material.dart';

/// 单选框组件
class AppRadio<T> extends StatelessWidget {
  final T value;
  final T? groupValue;
  final ValueChanged<T?>? onChanged;
  final Color? activeColor;
  final MaterialStateProperty<Color?>? fillColor;
  final MaterialStateProperty<Color?>? overlayColor;
  final double? splashRadius;
  final bool toggleable;
  final bool autofocus;
  final bool enabled;
  
  const AppRadio({
    super.key,
    required this.value,
    required this.groupValue,
    required this.onChanged,
    this.activeColor,
    this.fillColor,
    this.overlayColor,
    this.splashRadius,
    this.toggleable = false,
    this.autofocus = false,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    return Radio<T>(
      value: value,
      groupValue: groupValue,
      onChanged: enabled ? onChanged : null,
      activeColor: activeColor,
      fillColor: fillColor,
      overlayColor: overlayColor,
      splashRadius: splashRadius,
      toggleable: toggleable,
      autofocus: autofocus,
    );
  }
}

/// 单选框组组件
class AppRadioGroup<T> extends StatelessWidget {
  final List<AppRadioItem<T>> items;
  final T? value;
  final ValueChanged<T?>? onChanged;
  final Color? activeColor;
  final bool enabled;
  final EdgeInsets? padding;
  final EdgeInsets? itemPadding;
  final TextStyle? labelStyle;
  final bool vertical;
  
  const AppRadioGroup({
    super.key,
    required this.items,
    required this.value,
    required this.onChanged,
    this.activeColor,
    this.enabled = true,
    this.padding,
    this.itemPadding,
    this.labelStyle,
    this.vertical = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    Widget content = vertical
        ? Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: _buildItems(theme),
          )
        : Row(
            children: _buildItems(theme),
          );

    if (padding != null) {
      content = Padding(
        padding: padding!,
        child: content,
      );
    }

    return content;
  }

  List<Widget> _buildItems(ThemeData theme) {
    return items.map((item) {
      Widget radio = AppRadio<T>(
        value: item.value,
        groupValue: value,
        onChanged: enabled ? onChanged : null,
        activeColor: activeColor,
      );

      if (item.label != null) {
        radio = Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            radio,
            const SizedBox(width: 8),
            DefaultTextStyle(
              style: labelStyle ?? theme.textTheme.bodyMedium!,
              child: item.label!,
            ),
          ],
        );
      }

      if (itemPadding != null) {
        radio = Padding(
          padding: itemPadding!,
          child: radio,
        );
      }

      return radio;
    }).toList();
  }
}

/// 单选框项
class AppRadioItem<T> {
  final T value;
  final Widget? label;
  
  const AppRadioItem({
    required this.value,
    this.label,
  });
} 