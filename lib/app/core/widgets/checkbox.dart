import 'package:flutter/material.dart';

/// 复选框组件
class AppCheckbox extends StatelessWidget {
  final bool value;
  final ValueChanged<bool?>? onChanged;
  final Color? activeColor;
  final Color? checkColor;
  final bool enabled;
  final String? label;
  final TextStyle? labelStyle;
  final EdgeInsets? padding;
  
  const AppCheckbox({
    super.key,
    required this.value,
    this.onChanged,
    this.activeColor,
    this.checkColor,
    this.enabled = true,
    this.label,
    this.labelStyle,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultActiveColor = activeColor ?? theme.primaryColor;
    
    Widget checkbox = Checkbox(
      value: value,
      onChanged: enabled ? onChanged : null,
      activeColor: defaultActiveColor,
      checkColor: checkColor ?? Colors.white,
    );

    if (label != null) {
      checkbox = Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          checkbox,
          const SizedBox(width: 8),
          Text(
            label!,
            style: labelStyle ?? theme.textTheme.bodyMedium?.copyWith(
              color: enabled ? null : theme.disabledColor,
            ),
          ),
        ],
      );
    }

    if (padding != null) {
      checkbox = Padding(
        padding: padding!,
        child: checkbox,
      );
    }

    return checkbox;
  }
}

/// 复选框组组件
class AppCheckboxGroup extends StatelessWidget {
  final List<AppCheckboxItem> items;
  final List<String> value;
  final ValueChanged<List<String>>? onChanged;
  final Color? activeColor;
  final Color? checkColor;
  final bool enabled;
  final TextStyle? labelStyle;
  final EdgeInsets? padding;
  final EdgeInsets? itemPadding;
  final bool vertical;
  
  const AppCheckboxGroup({
    super.key,
    required this.items,
    required this.value,
    this.onChanged,
    this.activeColor,
    this.checkColor,
    this.enabled = true,
    this.labelStyle,
    this.padding,
    this.itemPadding,
    this.vertical = false,
  });

  @override
  Widget build(BuildContext context) {
    final checkboxes = items.map((item) {
      return AppCheckbox(
        value: value.contains(item.value),
        onChanged: (checked) {
          if (onChanged != null) {
            final newValue = List<String>.from(value);
            if (checked == true) {
              newValue.add(item.value);
            } else {
              newValue.remove(item.value);
            }
            onChanged!(newValue);
          }
        },
        activeColor: activeColor,
        checkColor: checkColor,
        enabled: enabled && item.enabled,
        label: item.label,
        labelStyle: labelStyle,
        padding: itemPadding,
      );
    }).toList();

    Widget group = vertical
        ? Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: checkboxes,
          )
        : Row(
            children: checkboxes,
          );

    if (padding != null) {
      group = Padding(
        padding: padding!,
        child: group,
      );
    }

    return group;
  }
}

/// 复选框项
class AppCheckboxItem {
  final String value;
  final String label;
  final bool enabled;
  
  const AppCheckboxItem({
    required this.value,
    required this.label,
    this.enabled = true,
  });
} 