import 'package:flutter/material.dart';
import '../../data/models/health_record.dart';

class HealthDataCard extends StatelessWidget {
  final HealthRecord data;
  final VoidCallback onTap;

  const HealthDataCard({
    Key? key,
    required this.data,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(16),
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    data.type,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    _formatDate(data.recordedAt),
                    style: TextStyle(
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              _buildDataGrid(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDataGrid() {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 2,
      ),
      itemCount: data.data.length,
      itemBuilder: (context, index) {
        final entry = data.data.entries.elementAt(index);
        return Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              entry.value.toString(),
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              entry.key,
              style: TextStyle(
                color: Colors.grey[600],
              ),
            ),
          ],
        );
      },
    );
  }

  String _formatDate(DateTime date) {
    return '${date.year}-${date.month}-${date.day}';
  }
} 