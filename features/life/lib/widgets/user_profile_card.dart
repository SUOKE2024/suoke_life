import 'package:flutter/material.dart';

class UserProfileCard extends StatelessWidget {
  const UserProfileCard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const CircleAvatar(
              radius: 40,
              backgroundImage: AssetImage('assets/images/user_avatar.png'),
            ),
            const SizedBox(height: 10),
            const Text(
              'John Doe',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 5),
            const Text('Software Engineer'),
          ],
        ),
      ),
    );
  }
} 