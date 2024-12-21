import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../../../services/upload_service.dart';

class FileUploadWidget extends StatefulWidget {
  final PlatformFile file;
  final Function(String) onUploadComplete;
  final Function(String)? onUploadError;
  final Function(double)? onUploadProgress;

  const FileUploadWidget({
    Key? key,
    required this.file,
    required this.onUploadComplete,
    this.onUploadError,
    this.onUploadProgress,
  }) : super(key: key);

  @override
  State<FileUploadWidget> createState() => _FileUploadWidgetState();
}

class _FileUploadWidgetState extends State<FileUploadWidget> {
  final _uploadService = Get.find<UploadService>();
  bool _isUploading = false;
  double _progress = 0;

  @override
  void initState() {
    super.initState();
    _startUpload();
  }

  Future<void> _startUpload() async {
    setState(() => _isUploading = true);

    try {
      final url = await _uploadService.uploadFile(
        widget.file,
        onProgress: (progress) {
          setState(() => _progress = progress);
          widget.onUploadProgress?.call(progress);
        },
      );
      widget.onUploadComplete(url);
    } catch (e) {
      widget.onUploadError?.call(e.toString());
    } finally {
      setState(() => _isUploading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Icon(
                _getFileIcon(),
                size: 40,
                color: Theme.of(context).primaryColor,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.file.name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _formatFileSize(widget.file.size),
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          if (_isUploading) ...[
            const SizedBox(height: 16),
            LinearProgressIndicator(value: _progress),
            const SizedBox(height: 8),
            Text(
              '上传中 ${(_progress * 100).toStringAsFixed(1)}%',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ],
        ],
      ),
    );
  }

  IconData _getFileIcon() {
    final extension = widget.file.extension?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return Icons.picture_as_pdf;
      case 'doc':
      case 'docx':
        return Icons.description;
      case 'xls':
      case 'xlsx':
        return Icons.table_chart;
      case 'ppt':
      case 'pptx':
        return Icons.slideshow;
      case 'zip':
      case 'rar':
        return Icons.folder_zip;
      default:
        return Icons.insert_drive_file;
    }
  }

  String _formatFileSize(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    if (bytes < 1024 * 1024 * 1024) {
      return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    }
    return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(1)} GB';
  }
} 