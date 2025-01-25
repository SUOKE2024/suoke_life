/// 文件选择器组件
class AppFilePicker extends StatelessWidget {
  final String title;
  final List<String>? allowedExtensions;
  final bool allowMultiple;
  final ValueChanged<List<File>>? onChanged;
  final String? cancelText;
  final String? confirmText;
  final Widget? placeholder;

  const AppFilePicker({
    super.key,
    required this.title,
    this.allowedExtensions,
    this.allowMultiple = false,
    this.onChanged,
    this.cancelText,
    this.confirmText,
    this.placeholder,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.7,
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
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  placeholder ??
                      const Icon(
                        Icons.upload_file,
                        size: 48,
                        color: Colors.grey,
                      ),
                  const SizedBox(height: 16),
                  AppButton(
                    text: '选择文件',
                    icon: Icons.add,
                    onPressed: () async {
                      final result = await FilePicker.platform.pickFiles(
                        type: allowedExtensions != null
                            ? FileType.custom
                            : FileType.any,
                        allowedExtensions: allowedExtensions,
                        allowMultiple: allowMultiple,
                      );

                      if (result != null) {
                        final files = result.paths
                            .map((path) => File(path!))
                            .toList();
                        onChanged?.call(files);
                        Navigator.of(context).pop();
                      }
                    },
                  ),
                  if (allowedExtensions != null) ...[
                    const SizedBox(height: 8),
                    Text(
                      '支持的格式: ${allowedExtensions!.join(', ')}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 显示文件选择器
  static Future<List<File>?> show(
    BuildContext context, {
    required String title,
    List<String>? allowedExtensions,
    bool allowMultiple = false,
    ValueChanged<List<File>>? onChanged,
    String? cancelText,
    String? confirmText,
    Widget? placeholder,
  }) {
    return showModalBottomSheet<List<File>>(
      context: context,
      builder: (_) => AppFilePicker(
        title: title,
        allowedExtensions: allowedExtensions,
        allowMultiple: allowMultiple,
        onChanged: onChanged,
        cancelText: cancelText,
        confirmText: confirmText,
        placeholder: placeholder,
      ),
    );
  }
} 