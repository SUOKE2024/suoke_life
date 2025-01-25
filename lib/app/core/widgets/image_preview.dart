/// 图片预览组件
class ImagePreview extends StatefulWidget {
  final List<String> images;
  final int initialIndex;
  final double? width;
  final double? height;
  final BoxFit? fit;
  final bool enableSwipe;
  final bool showIndicator;
  final Color? backgroundColor;
  final Widget Function(BuildContext, String, bool)? loadingBuilder;
  final Widget Function(BuildContext, Object, StackTrace?)? errorBuilder;
  final ValueChanged<int>? onPageChanged;

  const ImagePreview({
    super.key,
    required this.images,
    this.initialIndex = 0,
    this.width,
    this.height,
    this.fit,
    this.enableSwipe = true,
    this.showIndicator = true,
    this.backgroundColor,
    this.loadingBuilder,
    this.errorBuilder,
    this.onPageChanged,
  }) : assert(initialIndex >= 0 && initialIndex < images.length);

  @override
  State<ImagePreview> createState() => _ImagePreviewState();

  /// 显示图片预览
  static Future<T?> show<T>(
    BuildContext context, {
    required List<String> images,
    int initialIndex = 0,
    BoxFit? fit,
    bool enableSwipe = true,
    bool showIndicator = true,
    Color? backgroundColor,
    Widget Function(BuildContext, String, bool)? loadingBuilder,
    Widget Function(BuildContext, Object, StackTrace?)? errorBuilder,
    ValueChanged<int>? onPageChanged,
  }) {
    return showDialog<T>(
      context: context,
      builder: (_) => ImagePreview(
        images: images,
        initialIndex: initialIndex,
        fit: fit,
        enableSwipe: enableSwipe,
        showIndicator: showIndicator,
        backgroundColor: backgroundColor,
        loadingBuilder: loadingBuilder,
        errorBuilder: errorBuilder,
        onPageChanged: onPageChanged,
      ),
    );
  }
}

class _ImagePreviewState extends State<ImagePreview> {
  late PageController _controller;
  late int _currentIndex;

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.initialIndex;
    _controller = PageController(initialPage: _currentIndex);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Dialog.fullscreen(
      backgroundColor: widget.backgroundColor ?? Colors.black,
      child: Stack(
        children: [
          PageView.builder(
            controller: _controller,
            physics: widget.enableSwipe
                ? const AlwaysScrollableScrollPhysics()
                : const NeverScrollableScrollPhysics(),
            itemCount: widget.images.length,
            onPageChanged: (index) {
              setState(() => _currentIndex = index);
              widget.onPageChanged?.call(index);
            },
            itemBuilder: (context, index) {
              return InteractiveViewer(
                child: Center(
                  child: Image.network(
                    widget.images[index],
                    width: widget.width,
                    height: widget.height,
                    fit: widget.fit ?? BoxFit.contain,
                    loadingBuilder: widget.loadingBuilder,
                    errorBuilder: widget.errorBuilder,
                  ),
                ),
              );
            },
          ),
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: SafeArea(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.white),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                  if (widget.showIndicator)
                    Text(
                      '${_currentIndex + 1}/${widget.images.length}',
                      style: const TextStyle(color: Colors.white),
                    ),
                  const SizedBox(width: 48),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
} 