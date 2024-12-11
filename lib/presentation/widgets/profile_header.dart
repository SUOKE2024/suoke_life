import 'package:flutter/material.dart';

class ProfileHeader extends StatelessWidget {
  final Map<String, dynamic> userInfo;

  const ProfileHeader({
    super.key,
    required this.userInfo,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          CircleAvatar(
            radius: 48,
            backgroundColor: Theme.of(context).colorScheme.primary,
            child: Text(
              userInfo['username'][0].toUpperCase(),
              style: const TextStyle(
                fontSize: 32,
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            userInfo['username'],
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '会员等级: ${userInfo['role']}',
            style: TextStyle(
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildStatItem(context, '健康积分', '2380'),
              _buildDivider(),
              _buildStatItem(context, '运动天数', '168'),
              _buildDivider(),
              _buildStatItem(context, '饮品订单', '36'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(BuildContext context, String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            color: Colors.grey[600],
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Widget _buildDivider() {
    return Container(
      height: 24,
      width: 1,
      color: Colors.grey[300],
    );
  }
} 