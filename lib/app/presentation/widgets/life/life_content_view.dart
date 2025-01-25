import 'package:flutter/material.dart';
import '../../../domain/models/life_record.dart';

class LifeContentView extends StatelessWidget {
  final List<LifeRecord> records;

  const LifeContentView({
    super.key,
    required this.records,
  });

  @override
  Widget build(BuildContext context) {
    if (records.isEmpty) {
      return const Center(
        child: Text('暂无记录'),
      );
    }

    return ListView.builder(
      itemCount: records.length,
      itemBuilder: (context, index) {
        final record = records[index];
        return ListTile(
          title: Text(record.title),
          subtitle: Text(record.content),
          trailing: Text(record.type),
          onTap: () {
            // TODO: Navigate to record detail page
          },
        );
      },
    );
  }
} 