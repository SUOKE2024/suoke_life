import 'package:flutter/material.dart';
import '../../data/models/device_info.dart';
import 'package:timeago/timeago.dart' as timeago;

class DeviceListItem extends StatelessWidget {
  final DeviceInfo device;
  final bool isCurrentDevice;
  final VoidCallback onRename;
  final VoidCallback onRevoke;

  const DeviceListItem({
    Key? key,
    required this.device,
    required this.isCurrentDevice,
    required this.onRename,
    required this.onRevoke,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(
        _getDeviceIcon(),
        color: isCurrentDevice ? Colors.blue : null,
      ),
      title: Row(
        children: [
          Expanded(
            child: Text(device.deviceName),
          ),
          if (isCurrentDevice)
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: 8,
                vertical: 2,
              ),
              decoration: BoxDecoration(
                color: Colors.blue[100],
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                '当前设备',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.blue[700],
                ),
              ),
            ),
        ],
      ),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('${device.deviceModel} · ${device.osVersion}'),
          Text(
            '最后登录: ${timeago.format(device.lastLoginAt, locale: 'zh')}',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
      trailing: PopupMenuButton(
        itemBuilder: (context) => [
          const PopupMenuItem(
            value: 'rename',
            child: Row(
              children: [
                Icon(Icons.edit),
                SizedBox(width: 8),
                Text('重命名'),
              ],
            ),
          ),
          if (!isCurrentDevice)
            const PopupMenuItem(
              value: 'revoke',
              child: Row(
                children: [
                  Icon(Icons.delete),
                  SizedBox(width: 8),
                  Text('移除'),
                ],
              ),
            ),
        ],
        onSelected: (value) {
          switch (value) {
            case 'rename':
              onRename();
              break;
            case 'revoke':
              onRevoke();
              break;
          }
        },
      ),
    );
  }

  IconData _getDeviceIcon() {
    if (device.deviceModel.toLowerCase().contains('iphone')) {
      return Icons.phone_iphone;
    }
    if (device.deviceModel.toLowerCase().contains('ipad')) {
      return Icons.tablet_mac;
    }
    if (device.deviceModel.toLowerCase().contains('mac')) {
      return Icons.laptop_mac;
    }
    return Icons.phone_android;
  }
} 