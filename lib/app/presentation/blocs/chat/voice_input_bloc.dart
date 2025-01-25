import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:injectable/injectable.dart';
import 'voice_input_event.dart';
import 'voice_input_state.dart';

@injectable
class VoiceInputBloc extends Bloc<VoiceInputEvent, VoiceInputState> {
  VoiceInputBloc() : super(const VoiceInputInitial()) {
    on<VoiceInputEvent>((event, emit) async {
      if (event is VoiceInputStarted) {
        emit(const VoiceInputRecording());
      } else if (event is VoiceInputStopped) {
        emit(const VoiceInputProcessing());
      } else if (event is VoiceInputCancelled) {
        emit(const VoiceInputInitial());
      } else if (event is VoiceInputError) {
        emit(VoiceInputFailure(event.message));
      } else if (event is VoiceInputResult) {
        emit(VoiceInputSuccess(event.text));
      }
    });
  }
} 