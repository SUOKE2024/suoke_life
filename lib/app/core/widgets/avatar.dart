/// 头像组件
class AppAvatar extends StatelessWidget {
  final String? imageUrl;
  final String? name;
  final double size;
  final Color? backgroundColor;
  final Color? textColor;
  final double? fontSize;
  final BorderRadius? borderRadius;
  final BoxBorder? border;
  final List<BoxShadow>? shadows;
  final Widget? badge;
  final VoidCallback? onTap;
  final ImageProvider? placeholderImage;
  final Widget Function(BuildContext, Object, StackTrace?)? errorBuilder;

  const AppAvatar({
    super.key,
    this.imageUrl,
    this.name,
    this.size = 40,
    this.backgroundColor,
    this.textColor,
    this.fontSize,
    this.borderRadius,
    this.border,
    this.shadows,
    this.badge,
    this.onTap,
    this.placeholderImage,
    this.errorBuilder,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultBackgroundColor = backgroundColor ??
        Color(name?.hashCode ?? 0).withOpacity(0.2) ??
        theme.primaryColor.withOpacity(0.2);
    final defaultTextColor = textColor ?? theme.primaryColor;

    Widget avatar;
    if (imageUrl != null) {
      avatar = ClipRRect(
        borderRadius: borderRadius ?? BorderRadius.circular(size / 2),
        child: Image.network(
          imageUrl!,
          width: size,
          height: size,
          fit: BoxFit.cover,
          errorBuilder: errorBuilder ??
              (context, error, stackTrace) => _buildPlaceholder(
                    context,
                    defaultBackgroundColor,
                    defaultTextColor,
                  ),
        ),
      );
    } else {
      avatar = _buildPlaceholder(
        context,
        defaultBackgroundColor,
        defaultTextColor,
      );
    }

    if (onTap != null) {
      avatar = InkWell(
        onTap: onTap,
        borderRadius: borderRadius ?? BorderRadius.circular(size / 2),
        child: avatar,
      );
    }

    if (badge != null) {
      avatar = Stack(
        clipBehavior: Clip.none,
        children: [
          avatar,
          Positioned(
            right: -2,
            top: -2,
            child: badge!,
          ),
        ],
      );
    }

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        borderRadius: borderRadius ?? BorderRadius.circular(size / 2),
        border: border,
        boxShadow: shadows,
      ),
      child: avatar,
    );
  }

  Widget _buildPlaceholder(
    BuildContext context,
    Color backgroundColor,
    Color textColor,
  ) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: borderRadius ?? BorderRadius.circular(size / 2),
      ),
      child: Center(
        child: name != null
            ? Text(
                name!.length > 2 ? name!.substring(0, 2) : name!,
                style: TextStyle(
                  color: textColor,
                  fontSize: fontSize ?? size * 0.4,
                  fontWeight: FontWeight.bold,
                ),
              )
            : Icon(
                Icons.person,
                size: size * 0.6,
                color: textColor,
              ),
      ),
    );
  }
} 