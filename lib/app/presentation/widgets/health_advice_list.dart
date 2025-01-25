import 'package:flutter/material.dart';

class HealthAdviceList extends StatelessWidget {
  final List<Map<String, dynamic>> advices;
  final Function(Map<String, dynamic>) onTap;

  const HealthAdviceList({
    Key? key,
    required this.advices,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: advices.length,
      itemBuilder: (context, index) {
        final advice = advices[index];
        return Card(
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: Theme.of(context).primaryColor,
              child: Icon(
                _getIconData(advice['type']),
                color: Colors.white,
              ),
            ),
            title: Text(advice['title'] ?? ''),
            subtitle: Text(
              advice['content'] ?? '',
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            onTap: () => onTap(advice),
          ),
        );
      },
    );
  }

  IconData _getIconData(String? type) {
    switch (type) {
      case 'diet':
        return Icons.restaurant;
      case 'exercise':
        return Icons.fitness_center;
      case 'sleep':
        return Icons.bedtime;
      case 'medicine':
        return Icons.medical_services;
      default:
        return Icons.health_and_safety;
    }
  }
} 