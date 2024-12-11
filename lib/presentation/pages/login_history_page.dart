import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';
import '../../core/auth/models/login_log.dart';
import '../../core/auth/services/login_log_service.dart';
import 'package:share_plus/share_plus.dart';

class LoginHistoryPage extends StatelessWidget {
  const LoginHistoryPage({super.key});

  @override
  Widget build(BuildContext context) {
    final loginLogService = Get.find<LoginLogService>();
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('登录历史'),
        centerTitle: true,
        actions: [
          PopupMenuButton<String>(
            onSelected: (value) async {
              switch (value) {
                case 'export':
                  try {
                    final filePath = await loginLogService.exportLogs();
                    await Share.shareFiles([filePath]);
                  } catch (e) {
                    Get.snackbar('错误', '导出失败：${e.toString()}');
                  }
                  break;
                case 'clear':
                  final confirm = await Get.dialog<bool>(
                    AlertDialog(
                      title: const Text('清空登录历史'),
                      content: const Text('确定要清空所有登录历史记录吗？'),
                      actions: [
                        TextButton(
                          onPressed: () => Get.back(result: false),
                          child: const Text('取消'),
                        ),
                        TextButton(
                          onPressed: () => Get.back(result: true),
                          child: const Text('确定'),
                        ),
                      ],
                    ),
                  );
                  
                  if (confirm == true) {
                    await loginLogService.clearLogs();
                    Get.snackbar('提示', '登录历史已清空');
                  }
                  break;
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'export',
                child: Text('导出记录'),
              ),
              const PopupMenuItem(
                value: 'clear',
                child: Text('清空记录'),
              ),
            ],
          ),
        ],
      ),
      body: Obx(() {
        final logs = loginLogService.logs;
        
        if (logs.isEmpty) {
          return Center(
            child: Text(
              '暂无登录记录',
              style: TextStyle(
                fontSize: 16.sp,
                color: Colors.grey,
              ),
            ),
          );
        }
        
        return ListView.separated(
          padding: EdgeInsets.all(16.w),
          itemCount: logs.length,
          separatorBuilder: (context, index) => SizedBox(height: 16.h),
          itemBuilder: (context, index) {
            final log = logs[index];
            return _buildLogCard(log);
          },
        );
      }),
    );
  }
  
  Widget _buildLogCard(LoginLog log) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  log.loginType,
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Container(
                  padding: EdgeInsets.symmetric(
                    horizontal: 8.w,
                    vertical: 4.h,
                  ),
                  decoration: BoxDecoration(
                    color: log.isSuccess ? Colors.green[100] : Colors.red[100],
                    borderRadius: BorderRadius.circular(12.r),
                  ),
                  child: Text(
                    log.isSuccess ? '成功' : '失败',
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: log.isSuccess ? Colors.green : Colors.red,
                    ),
                  ),
                ),
              ],
            ),
            SizedBox(height: 8.h),
            Text(
              '设备：${log.deviceInfo}',
              style: TextStyle(
                fontSize: 14.sp,
                color: Colors.grey[600],
              ),
            ),
            SizedBox(height: 4.h),
            Text(
              '地点：${log.location}',
              style: TextStyle(
                fontSize: 14.sp,
                color: Colors.grey[600],
              ),
            ),
            SizedBox(height: 4.h),
            Text(
              '时间：${log.createdAt.toString()}',
              style: TextStyle(
                fontSize: 14.sp,
                color: Colors.grey[600],
              ),
            ),
            if (log.failureReason != null) ...[
              SizedBox(height: 8.h),
              Text(
                '失败原因：${log.failureReason}',
                style: TextStyle(
                  fontSize: 14.sp,
                  color: Colors.red,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
} 