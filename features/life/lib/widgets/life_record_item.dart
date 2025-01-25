import 'package:flutter/material.dart';

class LifeRecordItem extends StatelessWidget {
  final String title;
  final String time;
  final String description;

  const LifeRecordItem({
    Key? key,
    required this.title,
    required this.time,
    required this.description,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(title),
      subtitle: Text(description),
      trailing: Text(time),
    );
  }
} 