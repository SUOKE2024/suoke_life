import 'package:flutter/material.dart';
import '../../../data/models/group_file.dart';
import 'package:timeago/timeago.dart' as timeago;

class FileListItem extends StatelessWidget {
  final GroupFile file;
  final VoidCallback onTap;
  final VoidCallback onDownload;
  final VoidCallback onDelete;

  const FileListItem({
    Key? key,
    required this.file,
    required this.onTap,
    required this.onDownload,
    required this.onDelete,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: _buildFileIcon(),
      title: Text(
        file.name,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      subtitle: Row(
        children: [
          Text(
            _formatFileSize(file.size),
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(width: 8),
          Text(
            timeago.format(file.uploadTime, locale: 'zh'),
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
          if (file.downloadCount > 0) ...[
            const SizedBox(width: 8),
            Text(
              '${file.downloadCount}次下载',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ],
        ],
      ),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton(
            icon: const Icon(Icons.download),
            onPressed: onDownload,
            tooltip: '下载',
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: onDelete,
            tooltip: '删除',
          ),
        ],
      ),
      onTap: onTap,
    );
  }

  Widget _buildFileIcon() {
    IconData iconData;
    Color? color;

    if (file.isImage) {
      iconData = Icons.image;
      color = Colors.blue;
    } else if (file.isVideo) {
      iconData = Icons.video_file;
      color = Colors.red;
    } else if (file.isAudio) {
      iconData = Icons.audio_file;
      color = Colors.orange;
    } else if (file.isDocument) {
      switch (file.extension) {
        case 'pdf':
          iconData = Icons.picture_as_pdf;
          color = Colors.red;
          break;
        case 'doc':
        case 'docx':
          iconData = Icons.description;
          color = Colors.blue;
          break;
        case 'xls':
        case 'xlsx':
          iconData = Icons.table_chart;
          color = Colors.green;
          break;
        case 'ppt':
        case 'pptx':
          iconData = Icons.slideshow;
          color = Colors.orange;
          break;
        default:
          iconData = Icons.insert_drive_file;
          color = Colors.grey;
      }
    } else {
      iconData = Icons.insert_drive_file;
      color = Colors.grey;
    }

    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Icon(iconData, color: color),
    );
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
