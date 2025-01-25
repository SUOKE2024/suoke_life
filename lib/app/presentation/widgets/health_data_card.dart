import 'package:flutter/material.dart';
import '../../data/models/health_record.dart';

class HealthDataCard extends StatelessWidget {
  final HealthRecord? data;
  final VoidCallback onTap;

  const HealthDataCard({
    Key? key,
    this.data,
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
              const Text(
                '健康数据',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              if (data != null)
                Column(
                  children: [
                    _buildDataRow('身高', '${data!.height} cm'),
                    _buildDataRow('体重', '${data!.weight} kg'),
                    _buildDataRow('血压', '${data!.bloodPressure} mmHg'),
                    _buildDataRow('心率', '${data!.heartRate} bpm'),
                  ],
                )
              else
                const Center(
                  child: Text(
                    '暂无健康数据',
                    style: TextStyle(color: Colors.grey),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDataRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: Colors.grey,
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
} 