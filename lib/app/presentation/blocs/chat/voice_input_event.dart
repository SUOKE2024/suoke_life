abstract class VoiceInputEvent {
  const VoiceInputEvent();
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

class VoiceInputError extends VoiceInputEvent {
  final String message;
  const VoiceInputError(this.message);
}

class VoiceInputResult extends VoiceInputEvent {
  final String text;
  const VoiceInputResult(this.text);
} 