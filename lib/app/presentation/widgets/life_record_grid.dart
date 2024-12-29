import 'package:flutter/material.dart';
import 'package:timeago/timeago.dart' as timeago;

class LifeRecordGrid extends StatelessWidget {
  final List<Map<String, dynamic>> records;
  final Function(Map<String, dynamic>) onTap;

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
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        mainAxisSpacing: 16,
        crossAxisSpacing: 16,
        childAspectRatio: 0.8,
      ),
      itemCount: records.length,
      itemBuilder: (context, index) {
        final record = records[index];
        return Card(
          clipBehavior: Clip.antiAlias,
          child: InkWell(
            onTap: () => onTap(record),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (record['images']?.isNotEmpty ?? false)
                  AspectRatio(
                    aspectRatio: 1,
                    child: Image.network(
                      record['images'][0],
                      fit: BoxFit.cover,
                    ),
                  )
                else
                  AspectRatio(
                    aspectRatio: 1,
                    child: Container(
                      color: Theme.of(context).primaryColor.withOpacity(0.1),
                      child: Icon(
                        _getIconData(record['type']),
                        size: 48,
                        color: Theme.of(context).primaryColor,
                      ),
                    ),
                  ),
                Padding(
                  padding: const EdgeInsets.all(8),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        record['title'] ?? '',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        timeago.format(
                          DateTime.fromMillisecondsSinceEpoch(
                            record['created_at'] ?? 0,
                          ),
                          locale: 'zh',
                        ),
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  IconData _getIconData(String? type) {
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