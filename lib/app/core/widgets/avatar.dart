import 'package:flutter/material.dart';

/// 头像组件
class AppAvatar extends StatelessWidget {
  final String? text;
  final Widget? child;
  final String? imageUrl;
  final double? size;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final BorderRadius? borderRadius;
  final double? borderWidth;
  final Color? borderColor;
  final BoxFit? fit;
  final VoidCallback? onTap;

  const AppAvatar({
    super.key,
    this.text,
    this.child,
    this.imageUrl,
    this.size,
    this.backgroundColor,
    this.foregroundColor,
    this.borderRadius,
    this.borderWidth,
    this.borderColor,
    this.fit,
    this.onTap,
  }) : assert(text != null || child != null || imageUrl != null);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultSize = size ?? 40.0;
    final defaultBackgroundColor = backgroundColor ?? theme.primaryColor;
    final defaultForegroundColor = foregroundColor ?? Colors.white;
    final defaultBorderRadius =
        borderRadius ?? BorderRadius.circular(defaultSize / 2);

    Widget avatar;
    if (imageUrl != null) {
      avatar = ClipRRect(
        borderRadius: defaultBorderRadius,
        child: Image.network(
          imageUrl!,
          width: defaultSize,
          height: defaultSize,
          fit: fit ?? BoxFit.cover,
          errorBuilder: (context, error, stackTrace) {
            return _buildPlaceholder(
              size: defaultSize,
              backgroundColor: defaultBackgroundColor,
              foregroundColor: defaultForegroundColor,
            );
          },
        ),
      );
    } else if (child != null) {
      avatar = child!;
    } else {
      avatar = Container(
        width: defaultSize,
        height: defaultSize,
        decoration: BoxDecoration(
          color: defaultBackgroundColor,
          borderRadius: defaultBorderRadius,
        ),
        child: Center(
          child: Text(
            text!.length > 2 ? text!.substring(0, 2) : text!,
            style: TextStyle(
              color: defaultForegroundColor,
              fontSize: defaultSize * 0.4,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      );
    }

    if (borderWidth != null && borderWidth! > 0) {
      avatar = Container(
        decoration: BoxDecoration(
          borderRadius: defaultBorderRadius,
          border: Border.all(
            color: borderColor ?? theme.dividerColor,
            width: borderWidth!,
          ),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(
            (defaultBorderRadius).topLeft.x - borderWidth!,
          ),
          child: avatar,
        ),
      );
    }

    if (onTap != null) {
      avatar = InkWell(
        onTap: onTap,
        borderRadius: defaultBorderRadius,
        child: avatar,
      );
    }

    return SizedBox(
      width: defaultSize,
      height: defaultSize,
      child: avatar,
    );
  }

  Widget _buildPlaceholder({
    required double size,
    required Color backgroundColor,
    required Color foregroundColor,
  }) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: borderRadius ?? BorderRadius.circular(size / 2),
      ),
      child: Icon(
        Icons.person,
        color: foregroundColor,
        size: size * 0.6,
      ),
    );
  }
}

/// 头像组组件
class AppAvatarGroup extends StatelessWidget {
  final List<AppAvatar> avatars;
  final int? maxCount;
  final double? spacing;
  final double? size;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final BorderRadius? borderRadius;
  final double? borderWidth;
  final Color? borderColor;
  final VoidCallback? onMoreTap;

  const AppAvatarGroup({
    super.key,
    required this.avatars,
    this.maxCount,
    this.spacing,
    this.size,
    this.backgroundColor,
    this.foregroundColor,
    this.borderRadius,
    this.borderWidth,
    this.borderColor,
    this.onMoreTap,
  });

  @override
  Widget build(BuildContext context) {
    final displayAvatars = maxCount != null && avatars.length > maxCount!
        ? avatars.take(maxCount! - 1).toList()
        : avatars;
    final remainingCount = maxCount != null && avatars.length > maxCount!
        ? avatars.length - maxCount! + 1
        : 0;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        ...displayAvatars.map((avatar) {
          return Padding(
            padding: EdgeInsets.only(right: spacing ?? 8),
            child: AppAvatar(
              text: avatar.text,
              imageUrl: avatar.imageUrl,
              size: size ?? avatar.size,
              backgroundColor: backgroundColor ?? avatar.backgroundColor,
              foregroundColor: foregroundColor ?? avatar.foregroundColor,
              borderRadius: borderRadius ?? avatar.borderRadius,
              borderWidth: borderWidth ?? avatar.borderWidth,
              borderColor: borderColor ?? avatar.borderColor,
              fit: avatar.fit,
              onTap: avatar.onTap,
              child: avatar.child,
            ),
          );
        }),
        if (remainingCount > 0)
          AppAvatar(
            text: '+$remainingCount',
            size: size,
            backgroundColor: backgroundColor,
            foregroundColor: foregroundColor,
            borderRadius: borderRadius,
            borderWidth: borderWidth,
            borderColor: borderColor,
            onTap: onMoreTap,
          ),
      ],
    );
  }
}
