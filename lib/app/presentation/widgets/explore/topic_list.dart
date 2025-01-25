import 'package:flutter/material.dart';
import '../../../data/models/topic.dart';

class TopicList extends StatelessWidget {
  final List<Topic> topics;
  final Function(Topic) onTopicTap;

  const TopicList({
    Key? key,
    required this.topics,
    required this.onTopicTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: topics.length,
      separatorBuilder: (_, __) => const Divider(),
      itemBuilder: (context, index) {
        final topic = topics[index];
        return ListTile(
          leading: topic.imageUrl != null
              ? CircleAvatar(
                  backgroundImage: NetworkImage(topic.imageUrl!),
                )
              : CircleAvatar(
                  child: Text(topic.title[0].toUpperCase()),
                ),
          title: Text(topic.title),
          subtitle: Text(
            topic.description,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          trailing: const Icon(Icons.chevron_right),
          onTap: () => onTopicTap(topic),
        );
      },
    );
  }
} 