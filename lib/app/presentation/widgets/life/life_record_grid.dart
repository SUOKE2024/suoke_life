import 'package:flutter/material.dart';
import '../../../data/models/life_record.dart';
import 'package:timeago/timeago.dart' as timeago;

class LifeRecordGrid extends StatelessWidget {
  final List<LifeRecord> records;
  final Function(LifeRecord) onTap;

  const LifeRecordGrid({
    Key? key,
    required this.records,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        mainAxisSpacing: 16,
        crossAxisSpacing: 16,
        childAspectRatio: 1,
      ),
      itemCount: records.length,
      itemBuilder: (context, index) {
        final record = records[index];
        return Card(
          child: InkWell(
            onTap: () => onTap(record),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        _getIcon(record.type),
                        color: Theme.of(context).primaryColor,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          record.title,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Expanded(
                    child: Text(
                      record.content,
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    timeago.format(record.createdAt, locale: 'zh'),
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  IconData _getIcon(String type) {
    switch (type) {
      case 'daily':
        return Icons.calendar_today;
      case 'health':
        return Icons.favorite;
      case 'event':
        return Icons.event;
      case 'note':
        return Icons.note;
      default:
        return Icons.article;
    }
  }
} 