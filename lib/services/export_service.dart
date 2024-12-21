import 'package:get/get.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import 'package:excel/excel.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'dart:io';
import 'package:suoke_life/services/life_record_service.dart';

class ExportService extends GetxService {
  final LifeRecordService _recordService = Get.find();

  // 导出为Excel
  Future<void> exportToExcel() async {
    try {
      final excel = Excel.createExcel();
      final sheet = excel['生活记录'];

      // 添加表头
      sheet.appendRow(['时间', '内容', '标签', '图片']);

      // 添加数据
      final records = _recordService.getAllRecords();
      for (var record in records) {
        sheet.appendRow([
          record.time,
          record.content,
          record.tags.join(', '),
          record.image ?? '',
        ]);
      }

      // 保存文件
      final dir = await getApplicationDocumentsDirectory();
      final file = File('${dir.path}/生活记录.xlsx');
      await file.writeAsBytes(excel.encode()!);

      // 分享文件
      await Share.shareXFiles(
        [XFile(file.path)],
        text: '生活记录导出文件',
      );
    } catch (e) {
      Get.snackbar('错误', '导出Excel失败: $e');
    }
  }

  // 导出为PDF
  Future<void> exportToPDF() async {
    try {
      final pdf = pw.Document();
      final records = _recordService.getAllRecords();

      pdf.addPage(
        pw.MultiPage(
          pageFormat: PdfPageFormat.a4,
          build: (context) => [
            pw.Header(
              level: 0,
              child: pw.Text('生活记录', style: pw.TextStyle(fontSize: 24)),
            ),
            pw.SizedBox(height: 20),
            ...records.map((record) => pw.Column(
              crossAxisAlignment: pw.CrossAxisAlignment.start,
              children: [
                pw.Text(record.time, style: pw.TextStyle(fontSize: 14)),
                pw.SizedBox(height: 8),
                pw.Text(record.content),
                if (record.tags.isNotEmpty) ...[
                  pw.SizedBox(height: 8),
                  pw.Text('标签: ${record.tags.join(", ")}'),
                ],
                pw.Divider(),
                pw.SizedBox(height: 16),
              ],
            )).toList(),
          ],
        ),
      );

      // 保存文件
      final dir = await getApplicationDocumentsDirectory();
      final file = File('${dir.path}/生活记录.pdf');
      await file.writeAsBytes(await pdf.save());

      // 分享文件
      await Share.shareXFiles(
        [XFile(file.path)],
        text: '生活记录导出文件',
      );
    } catch (e) {
      Get.snackbar('错误', '导出PDF失败: $e');
    }
  }

  // 导出为Markdown
  Future<void> exportToMarkdown() async {
    try {
      final records = _recordService.getAllRecords();
      final buffer = StringBuffer();

      buffer.writeln('# 生活记录\n');
      
      for (var record in records) {
        buffer.writeln('## ${record.time}\n');
        buffer.writeln('${record.content}\n');
        if (record.tags.isNotEmpty) {
          buffer.writeln('标签: ${record.tags.join(", ")}\n');
        }
        if (record.image != null) {
          buffer.writeln('![图片](${record.image})\n');
        }
        buffer.writeln('---\n');
      }

      // 保存文件
      final dir = await getApplicationDocumentsDirectory();
      final file = File('${dir.path}/生活记录.md');
      await file.writeAsString(buffer.toString());

      // 分享文件
      await Share.shareXFiles(
        [XFile(file.path)],
        text: '生活记录导出文件',
      );
    } catch (e) {
      Get.snackbar('错误', '导出Markdown失败: $e');
    }
  }
} 