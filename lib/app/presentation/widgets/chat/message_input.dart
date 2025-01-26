import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/chat/chat_detail_bloc.dart';
import 'voice_input.dart';

class MessageInput extends StatefulWidget {
  const MessageInput({super.key});

  @override
  State<MessageInput> createState() => _MessageInputState();
}

class _MessageInputState extends State<MessageInput> {
  final _controller = TextEditingController();
  bool _isVoiceMode = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(8.0),
      child: Row(
        children: [
          IconButton(
            icon: Icon(_isVoiceMode ? Icons.keyboard : Icons.mic),
            onPressed: () {
              setState(() {
                _isVoiceMode = !_isVoiceMode;
              });
            },
          ),
          if (_isVoiceMode)
            Expanded(
              child: VoiceInput(
                onResult: (text) {
                  context
                      .read<ChatDetailBloc>()
                      .add(ChatDetailMessageSent(text));
                },
              ),
            )
          else
            Expanded(
              child: TextField(
                controller: _controller,
                decoration: const InputDecoration(
                  hintText: '输入消息...',
                  border: InputBorder.none,
                ),
                onSubmitted: (text) {
                  if (text.isNotEmpty) {
                    context.read<ChatDetailBloc>().add(
                          ChatDetailMessageSent(_controller.text),
                        );
                    _controller.clear();
                  }
                },
              ),
            ),
          IconButton(
            icon: const Icon(Icons.send),
            onPressed: () {
              if (_controller.text.isNotEmpty) {
                context.read<ChatDetailBloc>().add(
                      ChatDetailMessageSent(_controller.text),
                    );
                _controller.clear();
              }
            },
          ),
        ],
      ),
    );
  }
}
