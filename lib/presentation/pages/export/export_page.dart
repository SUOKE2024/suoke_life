import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/export_controller.dart';
import 'package:intl/intl.dart';

class ExportPage extends GetView<ExportController> {
  final dateFormat = DateFormat('yyyy-MM-dd');

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('导出数据'),
        actions: [
          // 导出按钮
          Obx(() => TextButton(
            onPressed: controller.isExporting.value ? null : controller.startExport,
            child: Text(
              '导出',
              style: TextStyle(
                color: controller.isExporting.value 
                  ? Colors.grey 
                  : Colors.white,
              ),
            ),
          )),
        ],
      ),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          // 导出格式选择
          Card(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: EdgeInsets.all(16),
                  child: Text(
                    '导出格式',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Divider(height: 1),
                Obx(() => Column(
                  children: controller.exportFormats.map((format) {
                    return RadioListTile<String>(
                      title: Text(format),
                      value: format,
                      groupValue: controller.selectedFormat.value,
                      onChanged: (value) {
                        controller.selectedFormat.value = value!;
                      },
                    );
                  }).toList(),
                )),
              ],
            ),
          ),

          SizedBox(height: 16),

          // 时间范围选择
          Card(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: EdgeInsets.all(16),
                  child: Text(
                    '时间范围',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Divider(height: 1),
                ListTile(
                  title: Text('开始日期'),
                  subtitle: Obx(() => Text(
                    controller.startDate.value != null
                      ? dateFormat.format(controller.startDate.value!)
                      : '请选择',
                  )),
                  trailing: Icon(Icons.calendar_today),
                  onTap: () => controller.selectStartDate(context),
                ),
                Divider(height: 1),
                ListTile(
                  title: Text('结束日期'),
                  subtitle: Obx(() => Text(
                    controller.endDate.value != null
                      ? dateFormat.format(controller.endDate.value!)
                      : '请选择',
                  )),
                  trailing: Icon(Icons.calendar_today),
                  onTap: () => controller.selectEndDate(context),
                ),
              ],
            ),
          ),

          SizedBox(height: 16),

          // 导出选项
          Card(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: EdgeInsets.all(16),
                  child: Text(
                    '导出选项',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Divider(height: 1),
                Obx(() => SwitchListTile(
                  title: Text('包含图片'),
                  subtitle: Text('导出记录中的图片'),
                  value: controller.includeImages.value,
                  onChanged: (value) => controller.includeImages.value = value,
                )),
                Divider(height: 1),
                Obx(() => SwitchListTile(
                  title: Text('包含标签'),
                  subtitle: Text('导出记录的标签信息'),
                  value: controller.includeTags.value,
                  onChanged: (value) => controller.includeTags.value = value,
                )),
                Divider(height: 1),
                Obx(() => SwitchListTile(
                  title: Text('包含统计数据'),
                  subtitle: Text('导出数据分析和图表'),
                  value: controller.includeAnalytics.value,
                  onChanged: (value) => controller.includeAnalytics.value = value,
                )),
              ],
            ),
          ),

          // 导出进度
          Obx(() {
            if (controller.isExporting.value) {
              return Padding(
                padding: EdgeInsets.symmetric(vertical: 16),
                child: Column(
                  children: [
                    LinearProgressIndicator(
                      value: controller.exportProgress.value,
                    ),
                    SizedBox(height: 8),
                    Text(
                      '导出进度: ${(controller.exportProgress.value * 100).toStringAsFixed(1)}%',
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                    TextButton(
                      onPressed: controller.cancelExport,
                      child: Text('取消导出'),
                    ),
                  ],
                ),
              );
            }
            return SizedBox.shrink();
          }),
        ],
      ),
    );
  }
} 