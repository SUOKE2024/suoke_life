import 'package:get/get.dart';
import 'package:suoke_life/services/export_service.dart';

class ExportController extends GetxController {
  final _exportService = Get.find<ExportService>();
  final isExporting = false.obs;

  Future<void> exportToExcel() async {
    try {
      isExporting.value = true;
      await _exportService.exportToExcel();
      Get.snackbar('成功', '数据已导出为Excel文件');
    } catch (e) {
      Get.snackbar('错误', '导出Excel失败: $e');
    } finally {
      isExporting.value = false;
    }
  }

  Future<void> exportToPdf() async {
    try {
      isExporting.value = true;
      await _exportService.exportToPdf();
      Get.snackbar('成功', '数据已导出为PDF文件');
    } catch (e) {
      Get.snackbar('错误', '导出PDF失败: $e');
    } finally {
      isExporting.value = false;
    }
  }

  Future<void> exportToMarkdown() async {
    try {
      isExporting.value = true;
      await _exportService.exportToMarkdown();
      Get.snackbar('成功', '数据已导出为Markdown文件');
    } catch (e) {
      Get.snackbar('错误', '导出Markdown失败: $e');
    } finally {
      isExporting.value = false;
    }
  }
} 