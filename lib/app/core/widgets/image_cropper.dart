/// 图片裁剪组件
class ImageCropper extends StatefulWidget {
  final String imagePath;
  final double? width;
  final double? height;
  final double aspectRatio;
  final bool lockAspectRatio;
  final bool enableZoom;
  final double minZoom;
  final double maxZoom;
  final Color? maskColor;
  final Color? strokeColor;
  final double strokeWidth;
  final BorderRadius? borderRadius;
  final ValueChanged<Rect>? onCropped;
  final VoidCallback? onCancel;
  final String? cancelText;
  final String? confirmText;

  const ImageCropper({
    super.key,
    required this.imagePath,
    this.width,
    this.height,
    this.aspectRatio = 1.0,
    this.lockAspectRatio = true,
    this.enableZoom = true,
    this.minZoom = 0.5,
    this.maxZoom = 3.0,
    this.maskColor,
    this.strokeColor,
    this.strokeWidth = 2.0,
    this.borderRadius,
    this.onCropped,
    this.onCancel,
    this.cancelText,
    this.confirmText,
  });

  @override
  State<ImageCropper> createState() => _ImageCropperState();
}

class _ImageCropperState extends State<ImageCropper> {
  late TransformationController _controller;
  late ValueNotifier<Rect> _cropRect;
  late ui.Image _image;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _controller = TransformationController();
    _cropRect = ValueNotifier(Rect.zero);
    _loadImage();
  }

  @override
  void dispose() {
    _controller.dispose();
    _cropRect.dispose();
    super.dispose();
  }

  Future<void> _loadImage() async {
    final file = File(widget.imagePath);
    final bytes = await file.readAsBytes();
    final codec = await ui.instantiateImageCodec(bytes);
    final frame = await codec.getNextFrame();
    setState(() {
      _image = frame.image;
      _isLoading = false;
      _initCropRect();
    });
  }

  void _initCropRect() {
    final imageWidth = _image.width.toDouble();
    final imageHeight = _image.height.toDouble();
    final imageRatio = imageWidth / imageHeight;
    final targetRatio = widget.lockAspectRatio ? widget.aspectRatio : imageRatio;

    double rectWidth, rectHeight;
    if (imageRatio > targetRatio) {
      rectHeight = imageHeight;
      rectWidth = rectHeight * targetRatio;
    } else {
      rectWidth = imageWidth;
      rectHeight = rectWidth / targetRatio;
    }

    final left = (imageWidth - rectWidth) / 2;
    final top = (imageHeight - rectHeight) / 2;
    _cropRect.value = Rect.fromLTWH(left, top, rectWidth, rectHeight);
  }

  void _handleCrop() {
    final rect = _cropRect.value;
    widget.onCropped?.call(rect);
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Expanded(
          child: Stack(
            fit: StackFit.expand,
            children: [
              InteractiveViewer(
                transformationController: _controller,
                minScale: widget.minZoom,
                maxScale: widget.maxZoom,
                panEnabled: true,
                scaleEnabled: widget.enableZoom,
                child: CustomPaint(
                  painter: _CropPainter(
                    image: _image,
                    cropRect: _cropRect,
                    maskColor: widget.maskColor ?? Colors.black54,
                    strokeColor: widget.strokeColor ?? Colors.white,
                    strokeWidth: widget.strokeWidth,
                    borderRadius: widget.borderRadius,
                  ),
                ),
              ),
              Positioned(
                left: 0,
                right: 0,
                bottom: 16,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    TextButton(
                      onPressed: widget.onCancel,
                      child: Text(widget.cancelText ?? '取消'),
                    ),
                    ElevatedButton(
                      onPressed: _handleCrop,
                      child: Text(widget.confirmText ?? '确定'),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _CropPainter extends CustomPainter {
  final ui.Image image;
  final ValueNotifier<Rect> cropRect;
  final Color maskColor;
  final Color strokeColor;
  final double strokeWidth;
  final BorderRadius? borderRadius;

  _CropPainter({
    required this.image,
    required this.cropRect,
    required this.maskColor,
    required this.strokeColor,
    required this.strokeWidth,
    this.borderRadius,
  }) : super(repaint: cropRect);

  @override
  void paint(Canvas canvas, Size size) {
    final rect = cropRect.value;
    final paint = Paint()..color = maskColor;

    // Draw mask
    canvas.drawRect(Offset.zero & size, paint);

    // Draw crop area
    if (borderRadius != null) {
      final rrect = RRect.fromRectAndCorners(
        rect,
        topLeft: borderRadius!.topLeft,
        topRight: borderRadius!.topRight,
        bottomLeft: borderRadius!.bottomLeft,
        bottomRight: borderRadius!.bottomRight,
      );
      canvas.drawRRect(rrect, Paint()..blendMode = BlendMode.clear);
      canvas.drawRRect(
        rrect,
        Paint()
          ..style = PaintingStyle.stroke
          ..color = strokeColor
          ..strokeWidth = strokeWidth,
      );
    } else {
      canvas.drawRect(rect, Paint()..blendMode = BlendMode.clear);
      canvas.drawRect(
        rect,
        Paint()
          ..style = PaintingStyle.stroke
          ..color = strokeColor
          ..strokeWidth = strokeWidth,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
} 