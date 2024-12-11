/// 标签组件
class AppChip extends StatelessWidget {
  final String label;
  final Color? color;
  final IconData? icon;
  final VoidCallback? onTap;
  final VoidCallback? onDelete;
  final bool selected;
  final bool outlined;

  const AppChip({
    super.key,
    required this.label,
    this.color,
    this.icon,
    this.onTap,
    this.onDelete,
    this.selected = false,
    this.outlined = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final chipColor = color ?? theme.primaryColor;

    Widget chip;
    if (outlined) {
      chip = OutlinedChip(
        label: Text(label),
        avatar: icon != null ? Icon(icon, size: 18) : null,
        onPressed: onTap,
        onDeleted: onDelete,
        side: BorderSide(color: chipColor),
        backgroundColor: selected ? chipColor.withOpacity(0.1) : null,
        labelStyle: TextStyle(color: chipColor),
      );
    } else {
      chip = Chip(
        label: Text(label),
        avatar: icon != null ? Icon(icon, size: 18) : null,
        onDeleted: onDelete,
        backgroundColor: selected ? chipColor : chipColor.withOpacity(0.1),
        labelStyle: TextStyle(
          color: selected ? Colors.white : chipColor,
        ),
      );
    }

    if (onTap != null) {
      return InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: chip,
      );
    }

    return chip;
  }
} 