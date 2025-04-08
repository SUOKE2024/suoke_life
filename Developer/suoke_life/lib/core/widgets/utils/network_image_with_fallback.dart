import 'package:flutter/material.dart';

/// 带错误处理和占位图的网络图片组件
class NetworkImageWithFallback extends StatelessWidget {
  /// 图片URL
  final String imageUrl;

  /// 适配方式
  final BoxFit fit;

  /// 图片宽度
  final double? width;

  /// 图片高度
  final double? height;

  /// 颜色滤镜
  final ColorFilter? colorFilter;

  /// 占位组件
  final Widget? placeholder;

  /// 错误处理组件
  final Widget? errorWidget;

  /// 加载指示器颜色
  final Color? loadingColor;

  /// 圆角
  final double borderRadius;

  const NetworkImageWithFallback({
    super.key,
    required this.imageUrl,
    this.fit = BoxFit.cover,
    this.width,
    this.height,
    this.colorFilter,
    this.placeholder,
    this.errorWidget,
    this.loadingColor,
    this.borderRadius = 0,
  });

  @override
  Widget build(BuildContext context) {
    Widget imageWidget = Image.network(
      imageUrl,
      fit: fit,
      width: width,
      height: height,
      frameBuilder: (context, child, frame, wasSynchronouslyLoaded) {
        if (wasSynchronouslyLoaded) {
          return child;
        }
        return AnimatedOpacity(
          opacity: frame == null ? 0 : 1,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
          child: frame == null && placeholder != null ? placeholder! : child,
        );
      },
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) {
          return child;
        }
        return placeholder ??
            Center(
              child: CircularProgressIndicator(
                value: loadingProgress.expectedTotalBytes != null
                    ? loadingProgress.cumulativeBytesLoaded /
                        loadingProgress.expectedTotalBytes!
                    : null,
                color: loadingColor ?? Theme.of(context).colorScheme.primary,
              ),
            );
      },
      errorBuilder: (context, error, stackTrace) {
        debugPrint('Error loading image: $imageUrl, error: $error');
        return errorWidget ??
            Container(
              width: width,
              height: height,
              color: Colors.grey.withAlpha(50),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.image_not_supported, color: Colors.grey),
                  SizedBox(height: 8),
                  Text('图片加载失败', style: TextStyle(color: Colors.grey)),
                ],
              ),
            );
      },
    );

    // 如果有颜色滤镜，应用ColorFiltered组件
    if (colorFilter != null) {
      imageWidget = ColorFiltered(
        colorFilter: colorFilter!,
        child: imageWidget,
      );
    }

    return ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      child: imageWidget,
    );
  }
}
