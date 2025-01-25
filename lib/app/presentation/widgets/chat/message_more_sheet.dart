import 'package:flutter/material.dart';

class MessageMoreSheet extends StatelessWidget {
  const MessageMoreSheet({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildItem(Icons.camera_alt, '拍照', () {}),
              _buildItem(Icons.photo, '相册', () {}),
              _buildItem(Icons.file_copy, '文件', () {}),
              _buildItem(Icons.phone, '通话', () {}),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildItem(IconData icon, String label, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 32),
          const SizedBox(height: 4),
          Text(label),
        ],
      ),
    );
  }
} 