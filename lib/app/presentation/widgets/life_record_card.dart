import 'package:flutter/material.dart';
import '../../data/models/life_record.dart';
import 'package:timeago/timeago.dart' as timeago;

class LifeRecordCard extends StatelessWidget {
  final LifeRecord record;
  final VoidCallback? onTap;

  const LifeRecordCard({
    Key? key,
    required this.record,
    this.onTap,
  }) : super(key: key);

  String _formatDate(DateTime date) {
    return timeago.format(date, locale: 'zh');
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
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
                    record.title,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  Text(
                    _formatDate(record.timestamp),
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                record.content,
                style: Theme.of(context).textTheme.bodyMedium,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
} 