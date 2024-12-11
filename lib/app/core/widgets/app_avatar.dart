/// 头像组件
class AppAvatar extends StatelessWidget {
  final String? imageUrl;
  final String? name;
  final double size;
  final Color? backgroundColor;
  final VoidCallback? onTap;

  const AppAvatar({
    super.key,
    this.imageUrl,
    this.name,
    this.size = 40,
    this.backgroundColor,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final child = imageUrl != null
        ? ClipOval(
            child: Image.network(
              imageUrl!,
              width: size,
              height: size,
              fit: BoxFit.cover,
              errorBuilder: (_, __, ___) => _buildPlaceholder(),
            ),
          )
        : _buildPlaceholder();

    if (onTap != null) {
      return InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(size / 2),
        child: child,
      );
    }

    return child;
  }

  Widget _buildPlaceholder() {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: backgroundColor ?? Colors.grey[300],
        shape: BoxShape.circle,
      ),
      child: name != null
          ? Center(
              child: Text(
                name!.substring(0, 1).toUpperCase(),
                style: TextStyle(
                  fontSize: size * 0.4,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            )
          : Icon(
              Icons.person_outline,
              size: size * 0.6,
              color: Colors.white,
            ),
    );
  }
} 