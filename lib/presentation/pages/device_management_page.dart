import 'package:flutter/material.dart';

class DeviceManagementPage extends StatefulWidget {
  const DeviceManagementPage({super.key});

  @override
  State<DeviceManagementPage> createState() => _DeviceManagementPageState();
}

class _DeviceManagementPageState extends State<DeviceManagementPage> {
  bool _isLoading = true;
  final List<_DeviceInfo> _devices = [];

  @override
  void initState() {
    super.initState();
    _loadDevices();
  }

  Future<void> _loadDevices() async {
    setState(() => _isLoading = true);
    try {
      // TODO: 从服务器获取设备列表
      await Future.delayed(const Duration(seconds: 1));
      setState(() {
        _devices.addAll([
          _DeviceInfo(
            name: 'iPhone 13',
            type: 'iOS',
            location: '上海',
            lastLoginTime: DateTime.now().subtract(const Duration(minutes: 5)),
            isCurrentDevice: true,
          ),
          _DeviceInfo(
            name: 'MacBook Pro',
            type: 'macOS',
            location: '上海',
            lastLoginTime: DateTime.now().subtract(const Duration(hours: 2)),
            isCurrentDevice: false,
          ),
          _DeviceInfo(
            name: 'iPad Pro',
            type: 'iPadOS',
            location: '北京',
            lastLoginTime: DateTime.now().subtract(const Duration(days: 1)),
            isCurrentDevice: false,
          ),
        ]);
      });
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _removeDevice(_DeviceInfo device) async {
    if (device.isCurrentDevice) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('无法移除当前设备')),
      );
      return;
    }

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('移除设备'),
        content: Text('确定要移除设备"${device.name}"吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('确定'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    setState(() => _isLoading = true);
    try {
      // TODO: 调用服务器移除设备
      await Future.delayed(const Duration(seconds: 1));
      setState(() {
        _devices.remove(device);
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('设备已移除')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('设备管理'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadDevices,
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: _devices.length,
                itemBuilder: (context, index) {
                  final device = _devices[index];
                  return Card(
                    child: ListTile(
                      leading: Icon(
                        device.type == 'iOS' || device.type == 'iPadOS'
                            ? Icons.phone_iphone
                            : Icons.laptop_mac,
                        size: 32,
                      ),
                      title: Row(
                        children: [
                          Text(device.name),
                          if (device.isCurrentDevice) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.green[100],
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: const Text(
                                '当前设备',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.green,
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('登录地点：${device.location}'),
                          Text(
                            '最后登录：${_formatDateTime(device.lastLoginTime)}',
                          ),
                        ],
                      ),
                      trailing: device.isCurrentDevice
                          ? null
                          : IconButton(
                              icon: const Icon(Icons.delete_outline),
                              onPressed: () => _removeDevice(device),
                            ),
                    ),
                  );
                },
              ),
            ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inMinutes < 1) {
      return '刚刚';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}分钟前';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}小时前';
    } else if (difference.inDays < 30) {
      return '${difference.inDays}天前';
    } else {
      return '${dateTime.year}-${dateTime.month}-${dateTime.day}';
    }
  }
}

class _DeviceInfo {
  final String name;
  final String type;
  final String location;
  final DateTime lastLoginTime;
  final bool isCurrentDevice;

  const _DeviceInfo({
    required this.name,
    required this.type,
    required this.location,
    required this.lastLoginTime,
    required this.isCurrentDevice,
  });
} 