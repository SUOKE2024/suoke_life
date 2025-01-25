import 'package:equatable/equatable.dart';

abstract class VoiceInputState extends Equatable {
  const VoiceInputState();

  @override
  List<Object> get props => [];
}

class VoiceInputInitial extends VoiceInputState {
  const VoiceInputInitial();
}

class VoiceInputRecording extends VoiceInputState {
  const VoiceInputRecording();
}

class VoiceInputSuccess extends VoiceInputState {
  final String text;
  const VoiceInputSuccess(this.text);

  @override
  List<Object> get props => [text];
}

class VoiceInputError extends VoiceInputState {
  final String message;
  const VoiceInputError(this.message);

  @override
  List<Object> get props => [message];
} 