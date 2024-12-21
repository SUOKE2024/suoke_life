import 'package:share_plus/share_plus.dart';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:suoke_life/data/models/life_record.dart';

class ShareService {
  // 分享生活记录
  Future<void> shareLifeRecord(LifeRecord record) async {
    String text = '${record.time}\n\n${record.content}';
    
    if (record.tags.isNotEmpty) {
      text += '\n\n标签: ${record.tags.join(', ')}';
    }

    if (record.image != null) {
      final file = File(record.image!);
      if (await file.exists()) {
        // 分享文本和图片
        await Share.shareXFiles(
          [XFile(record.image!)],
          text: text,
        );
      } else {
        // 只分享文本
        await Share.share(text);
      }
    } else {
      // 只分享文本
      await Share.share(text);
    }
  }
} 