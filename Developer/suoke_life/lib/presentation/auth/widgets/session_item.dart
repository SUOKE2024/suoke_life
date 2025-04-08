import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/domain/usecases/auth_usecases.dart';

/// 会话项目组件
class SessionItem extends StatelessWidget {
  final UserSession session;
  final VoidCallback onTerminate;
  
  const SessionItem({
    Key? key, 
    required this.session,
    required this.onTerminate,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    // 格式化最后活跃时间
    final dateFormat = DateFormat('yyyy-MM-dd HH:mm');
    final lastActiveFormatted = dateFormat.format(session.lastActive);
    
    // 计算距离上次活跃的时间差
    final now = DateTime.now();
    final difference = now.difference(session.lastActive);
    String timeAgo = '';
    
    if (difference.inMinutes < 1) {
      timeAgo = '刚刚';
    } else if (difference.inMinutes < 60) {
      timeAgo = '${difference.inMinutes}分钟前';
    } else if (difference.inHours < 24) {
      timeAgo = '${difference.inHours}小时前';
    } else {
      timeAgo = '${difference.inDays}天前';
    }
    
    // 获取设备图标
    IconData deviceIcon = Icons.devices_other;
    if (session.deviceName.toLowerCase().contains('iphone') || 
        session.deviceName.toLowerCase().contains('ios')) {
      deviceIcon = Icons.phone_iphone;
    } else if (session.deviceName.toLowerCase().contains('android')) {
      deviceIcon = Icons.phone_android;
    } else if (session.deviceName.toLowerCase().contains('mac')) {
      deviceIcon = Icons.laptop_mac;
    } else if (session.deviceName.toLowerCase().contains('windows')) {
      deviceIcon = Icons.laptop_windows;
    } else if (session.deviceName.toLowerCase().contains('tablet')) {
      deviceIcon = Icons.tablet_mac;
    }
    
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: session.isCurrent ? AppColors.primary.withAlpha(100) : Colors.transparent,
          width: 1.5,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: session.isCurrent 
                        ? AppColors.primary.withAlpha(40)
                        : Colors.grey.withAlpha(40),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    deviceIcon,
                    color: session.isCurrent ? AppColors.primary : Colors.grey,
                    size: 28,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              session.deviceName,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          if (session.isCurrent)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                color: AppColors.primary,
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: const Text(
                                '当前设备',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 12,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '最后活跃：$timeAgo',
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Divider(),
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(
                  Icons.location_on_outlined,
                  size: 16,
                  color: Colors.grey[600],
                ),
                const SizedBox(width: 4),
                Text(
                  session.location,
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 13,
                  ),
                ),
                const SizedBox(width: 16),
                Icon(
                  Icons.access_time,
                  size: 16,
                  color: Colors.grey[600],
                ),
                const SizedBox(width: 4),
                Text(
                  lastActiveFormatted,
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 13,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(
                  Icons.wifi,
                  size: 16,
                  color: Colors.grey[600],
                ),
                const SizedBox(width: 4),
                Text(
                  'IP: ${session.ipAddress}',
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 13,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (!session.isCurrent) // 只有非当前会话才显示终止按钮
              SizedBox(
                width: double.infinity,
                child: TextButton.icon(
                  onPressed: onTerminate,
                  icon: const Icon(Icons.logout, size: 18),
                  label: const Text('终止此会话'),
                  style: TextButton.styleFrom(
                    foregroundColor: Colors.red,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
} 