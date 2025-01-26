import 'package:flutter/material.dart';
import 'package:suoke_life/features/home/lib/chat_list_item.dart';
import 'package:go_router/go_router.dart';
import 'package:suoke_life/libs/ui_components/lib/navigation/bottom_navigation_bar.dart';

class ChatPage extends StatefulWidget {
  const ChatPage({Key? key}) : super(key: key);

  @override
  _ChatPageState createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  int _currentIndex = 0;

  void _onTabTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Chats'),
      ),
      body: ListView(
        children: const [
          ChatListItem(
            title: 'Xiaoai',
            lastMessage: 'Hello, how can I help you?',
            time: '10:00 AM',
          ),
          ChatListItem(
            title: 'Xiaoke',
            lastMessage: 'What are you doing today?',
            time: 'Yesterday',
          ),
          ChatListItem(
            title: 'Laoke',
            lastMessage: 'What is the meaning of life?',
            time: '2 days ago',
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          context.go('/chat_interaction');
        },
        child: const Icon(Icons.add),
      ),
      bottomNavigationBar: AppBottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
      ),
    );
  }
}
