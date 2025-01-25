import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:path/path.dart' as path;
import 'package:mime/mime.dart';

class FilePickerWidget extends StatelessWidget {
  final Function(PlatformFile) onFilePicked;
  final List<String>? allowedExtensions;
  final FileType type;
  final bool allowMultiple;
  final Widget? child;

  const FilePickerWidget({
    Key? key,
    required this.onFilePicked,
    this.allowedExtensions,
    this.type = FileType.any,
    this.allowMultiple = false,
    this.child,
  }) : super(key: key);

  Future<void> _pickFile() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: type,
        allowedExtensions: allowedExtensions,
        allowMultiple: allowMultiple,
      );

      if (result != null && result.files.isNotEmpty) {
        onFilePicked(result.files.first);
      }
    } catch (e) {
      debugPrint('文件选择失败: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: _pickFile,
      child: child ?? const Icon(Icons.attach_file),
    );
  }
} 