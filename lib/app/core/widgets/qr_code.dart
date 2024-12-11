/// 二维码组件
class QRCode extends StatelessWidget {
  final String data;
  final double? size;
  final Color? foregroundColor;
  final Color? backgroundColor;
  final int version;
  final int errorCorrectionLevel;
  final Widget? embeddedImage;
  final double? embeddedImageSize;
  final BoxFit? embeddedImageFit;
  final EdgeInsets? embeddedImagePadding;
  final BorderRadius? borderRadius;
  final BoxBorder? border;
  final List<BoxShadow>? shadows;

  const QRCode({
    super.key,
    required this.data,
    this.size,
    this.foregroundColor,
    this.backgroundColor,
    this.version = 4,
    this.errorCorrectionLevel = QrErrorCorrectLevel.L,
    this.embeddedImage,
    this.embeddedImageSize,
    this.embeddedImageFit,
    this.embeddedImagePadding,
    this.borderRadius,
    this.border,
    this.shadows,
  });

  @override
  Widget build(BuildContext context) {
    final defaultSize = size ?? 200.0;
    final defaultForegroundColor = foregroundColor ?? Colors.black;
    final defaultBackgroundColor = backgroundColor ?? Colors.white;
    final imageSize = embeddedImageSize ?? defaultSize * 0.2;

    Widget qrCode = QrImage(
      data: data,
      size: defaultSize,
      version: version,
      errorCorrectionLevel: errorCorrectionLevel,
      foregroundColor: defaultForegroundColor,
      backgroundColor: defaultBackgroundColor,
      padding: EdgeInsets.zero,
      embeddedImage: embeddedImage != null
          ? (embeddedImage is Image
              ? (embeddedImage as Image).image
              : null)
          : null,
      embeddedImageStyle: QrEmbeddedImageStyle(
        size: Size(imageSize, imageSize),
      ),
    );

    if (embeddedImage != null && embeddedImage is! Image) {
      qrCode = Stack(
        alignment: Alignment.center,
        children: [
          qrCode,
          Padding(
            padding: embeddedImagePadding ?? EdgeInsets.zero,
            child: SizedBox(
              width: imageSize,
              height: imageSize,
              child: embeddedImage,
            ),
          ),
        ],
      );
    }

    if (borderRadius != null || border != null || shadows != null) {
      qrCode = Container(
        decoration: BoxDecoration(
          color: defaultBackgroundColor,
          borderRadius: borderRadius,
          border: border,
          boxShadow: shadows,
        ),
        child: ClipRRect(
          borderRadius: borderRadius ?? BorderRadius.zero,
          child: qrCode,
        ),
      );
    }

    return qrCode;
  }
} 