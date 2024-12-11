/// 图片选择器组件
class AppImagePicker extends StatelessWidget {
  final String title;
  final bool allowMultiple;
  final bool enableCamera;
  final int? maxImages;
  final ValueChanged<List<File>>? onChanged;
  final String? cancelText;
  final List<String>? initialImages;
  final double? maxWidth;
  final double? maxHeight;
  final int? imageQuality;

  const AppImagePicker({
    super.key,
    required this.title,
    this.allowMultiple = false,
    this.enableCamera = true,
    this.maxImages,
    this.onChanged,
    this.cancelText,
    this.initialImages,
    this.maxWidth,
    this.maxHeight,
    this.imageQuality,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.3,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 标题栏
          Container(
            padding: AppStyles.padding,
            child: Row(
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const Spacer(),
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: Text(cancelText ?? '取消'),
                ),
              ],
            ),
          ),
          const Divider(height: 1),
          // 选择按钮
          Expanded(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildOption(
                  context,
                  icon: Icons.photo_library,
                  label: '相册',
                  onTap: () => _pickImage(context, ImageSource.gallery),
                ),
                if (enableCamera)
                  _buildOption(
                    context,
                    icon: Icons.camera_alt,
                    label: '相机',
                    onTap: () => _pickImage(context, ImageSource.camera),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOption(
    BuildContext context, {
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 40),
          const SizedBox(height: 8),
          Text(label),
        ],
      ),
    );
  }

  Future<void> _pickImage(BuildContext context, ImageSource source) async {
    try {
      final picker = ImagePicker();
      if (allowMultiple && source == ImageSource.gallery) {
        final images = await picker.pickMultiImage(
          maxWidth: maxWidth,
          maxHeight: maxHeight,
          imageQuality: imageQuality,
        );
        if (images.isNotEmpty) {
          final files = images.map((xFile) => File(xFile.path)).toList();
          onChanged?.call(files);
          Navigator.of(context).pop();
        }
      } else {
        final image = await picker.pickImage(
          source: source,
          maxWidth: maxWidth,
          maxHeight: maxHeight,
          imageQuality: imageQuality,
        );
        if (image != null) {
          onChanged?.call([File(image.path)]);
          Navigator.of(context).pop();
        }
      }
    } catch (e) {
      debugPrint('Error picking image: $e');
    }
  }

  /// 显示图片选择器
  static Future<List<File>?> show(
    BuildContext context, {
    required String title,
    bool allowMultiple = false,
    bool enableCamera = true,
    int? maxImages,
    ValueChanged<List<File>>? onChanged,
    String? cancelText,
    List<String>? initialImages,
    double? maxWidth,
    double? maxHeight,
    int? imageQuality,
  }) {
    return showModalBottomSheet<List<File>>(
      context: context,
      builder: (_) => AppImagePicker(
        title: title,
        allowMultiple: allowMultiple,
        enableCamera: enableCamera,
        maxImages: maxImages,
        onChanged: onChanged,
        cancelText: cancelText,
        initialImages: initialImages,
        maxWidth: maxWidth,
        maxHeight: maxHeight,
        imageQuality: imageQuality,
      ),
    );
  }
} 