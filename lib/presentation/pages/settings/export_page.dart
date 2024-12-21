import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/export_controller.dart';

class ExportPage extends GetView<ExportController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('导出数据'),
      ),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          _buildExportCard(
            title: '导出为Excel',
            subtitle: '导出为Excel表格格式',
            icon: Icons.table_chart,
            onTap: controller.exportToExcel,
          ),
          SizedBox(height: 16),
          _buildExportCard(
            title: '导出为PDF',
            subtitle: '导出为PDF文档格式',
            icon: Icons.picture_as_pdf,
            onTap: controller.exportToPdf,
          ),
          SizedBox(height: 16),
          _buildExportCard(
            title: '导出为Markdown',
            subtitle: '导出为Markdown文本格式',
            icon: Icons.text_fields,
            onTap: controller.exportToMarkdown,
          ),
        ],
      ),
    );
  }

  Widget _buildExportCard({
    required String title,
    required String subtitle,
    required IconData icon,
    required VoidCallback onTap,
  }) {
    return Card(
      child: ListTile(
        leading: Icon(icon, size: 32),
        title: Text(title),
        subtitle: Text(subtitle),
        trailing: Icon(Icons.arrow_forward_ios, size: 16),
        onTap: onTap,
      ),
    );
  }
} 