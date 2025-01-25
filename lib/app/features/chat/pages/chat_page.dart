import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';

@RoutePage()
class ChatPage extends StatelessWidget {
  final String assistantId;
  
  const ChatPage({
    @PathParam('assistantId') required this.assistantId,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(assistantId == 'xiaoke' ? '小克' : '小艾'),
      ),
      body: Center(
        child: Text('与 $assistantId 对话'),
      ),
    );
  }
} 