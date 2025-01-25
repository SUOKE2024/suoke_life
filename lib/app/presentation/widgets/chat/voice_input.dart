import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/voice/voice_input_bloc.dart';
import '../../blocs/voice/voice_input_event.dart';
import '../../blocs/voice/voice_input_state.dart';

class VoiceInput extends StatelessWidget {
  const VoiceInput({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => VoiceInputBloc(),
      child: BlocConsumer<VoiceInputBloc, VoiceInputState>(
        listener: (context, state) {
          if (state is VoiceInputError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(state.message)),
            );
          }
        },
        builder: (context, state) {
          return Container(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: GestureDetector(
                    onLongPressStart: (_) {
                      context.read<VoiceInputBloc>().add(
                            const VoiceInputStarted(),
                          );
                    },
                    onLongPressEnd: (_) {
                      context.read<VoiceInputBloc>().add(
                            const VoiceInputStopped(),
                          );
                    },
                    child: Container(
                      height: 50,
                      decoration: BoxDecoration(
                        color: Colors.grey[200],
                        borderRadius: BorderRadius.circular(25),
                      ),
                      child: Center(
                        child: Text(
                          state is VoiceInputRecording
                              ? '松开发送'
                              : '按住说话',
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
} 