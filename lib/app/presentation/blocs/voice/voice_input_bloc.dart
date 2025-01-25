import 'package:flutter_bloc/flutter_bloc.dart';
import 'voice_input_event.dart';
import 'voice_input_state.dart';

class VoiceInputBloc extends Bloc<VoiceInputEvent, VoiceInputState> {
  VoiceInputBloc() : super(const VoiceInputInitial()) {
    on<VoiceInputStarted>(_onStarted);
    on<VoiceInputStopped>(_onStopped);
    on<VoiceInputCancelled>(_onCancelled);
  }

  void _onStarted(VoiceInputStarted event, Emitter<VoiceInputState> emit) {
    emit(const VoiceInputRecording());
  }

  void _onStopped(VoiceInputStopped event, Emitter<VoiceInputState> emit) {
    // TODO: Implement voice recognition
    emit(const VoiceInputSuccess('语音识别结果'));
  }

  void _onCancelled(VoiceInputCancelled event, Emitter<VoiceInputState> emit) {
    emit(const VoiceInputInitial());
  }
} 