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
          child: ListTile(
            leading: CircleAvatar(
              child: Icon(_getIcon(advice['type'])),
            ),
            title: Text(advice['title']),
            subtitle: Text(
              advice['description'],
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => onTap(advice),
          ),
        );
      },
    );
  }

  IconData _getIcon(String type) {
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