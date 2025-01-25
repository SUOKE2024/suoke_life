import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:provider/provider.dart';
import '../../blocs/chat/chat_detail_bloc.dart';
import '../../blocs/chat/chat_detail_event.dart';
import '../../blocs/chat/chat_detail_state.dart';
import '../../../domain/repositories/chat_repository.dart';

@RoutePage()
class ChatDetailPage extends StatefulWidget {
  final String chatId;
  
  const ChatDetailPage({
    Key? key,
    @PathParam('id') required this.chatId,
  }) : super(key: key);

  @override
  State<ChatDetailPage> createState() => _ChatDetailPageState();
}

class _ChatDetailPageState extends State<ChatDetailPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ChatDetailBloc>().add(LoadChatDetailEvent(widget.chatId));
    });
  }

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<ChatDetailBloc, ChatDetailState>(
      builder: (context, state) {
        return Scaffold(
          appBar: AppBar(
            title: Text(
              state is ChatDetailLoaded ? state.chatInfo.title : '聊天'
            ),
          ),
          body: _buildBody(state),
        );
      },
    );
  }

  Widget _buildBody(ChatDetailState state) {
    if (state is ChatDetailLoading || state is ChatDetailInitial) {
      return const Center(child: CircularProgressIndicator());
    }

    if (state is ChatDetailError) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(state.message),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                context.read<ChatDetailBloc>().add(LoadChatDetailEvent(widget.chatId));
              },
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    if (state is ChatDetailLoaded) {
      if (state.messages.isEmpty) {
        return const Center(child: Text('暂无消息'));
      }
      
      return ListView.builder(
        itemCount: state.messages.length,
        itemBuilder: (context, index) {
          final message = state.messages[index];
          return ListTile(
            title: Text(message.content),
            subtitle: Text(message.timestamp.toString()),
          );
        },
      );
    }

    return const SizedBox();
  }
} 