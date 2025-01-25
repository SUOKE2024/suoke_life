import 'package:equatable/equatable.dart';

abstract class VoiceInputEvent extends Equatable {
  const VoiceInputEvent();

  @override
  List<Object> get props => [];
}

class VoiceInputStarted extends VoiceInputEvent {
  const VoiceInputStarted();
}

class VoiceInputStopped extends VoiceInputEvent {
  const VoiceInputStopped();
}

class VoiceInputCancelled extends VoiceInputEvent {
  const VoiceInputCancelled();
} 