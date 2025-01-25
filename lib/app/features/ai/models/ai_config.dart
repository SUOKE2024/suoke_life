class AIConfig {
  final String model;
  final double temperature;
  final Map<String, dynamic> parameters;

  AIConfig({
    required this.model,
    this.temperature = 0.7,
    this.parameters = const {},
  });

  static AIConfig forType(String type) {
    switch (type) {
      case 'xiao_ai':
        return AIConfig(
          model: 'gpt-3.5-turbo',
          temperature: 0.7,
          parameters: {
            'max_tokens': 1000,
            'presence_penalty': 0.6,
          },
        );
      default:
        return AIConfig(model: 'gpt-3.5-turbo');
    }
  }
} 