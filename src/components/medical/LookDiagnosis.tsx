import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Animated,
  Alert,
} from 'react-native';
import {
  Card,
  Text,
  useTheme,
  ProgressBar,
  IconButton,
  List,
  Divider,
  Badge,
  ActivityIndicator,
  Chip,
} from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

interface LookDiagnosisProps {
  onComplete?: (results: LookDiagnosisResults) => void;
  onCancel?: () => void;
  onSkip?: () => void;
}

interface LookDiagnosisResults {
  face?: LookAnalysisData;
  tongue?: LookAnalysisData;
  eyes?: LookAnalysisData;
}

interface LookAnalysisData {
  complexion?: string;
  features?: string[];
  constitution?: string;
  suggestions?: string[];
  local_fallback?: boolean;
}

const LookDiagnosis: React.FC<LookDiagnosisProps> = ({ onComplete, onCancel, onSkip }) => {
  const theme = useTheme();
  const [currentStep, setCurrentStep] = useState(0);
  const [progress] = useState(new Animated.Value(0));
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [faceAnalysis, setFaceAnalysis] = useState<LookAnalysisData | null>(null);
  const [tongueAnalysis, setTongueAnalysis] = useState<LookAnalysisData | null>(null);
  const [eyeAnalysis, setEyeAnalysis] = useState<LookAnalysisData | null>(null);
  const [showAgentChat, setShowAgentChat] = useState(false);

  const steps = [
    {
      id: 'face',
      title: '面色观察',
      icon: 'face-man',
      description: '观察面部气色、神态',
      tips: [
        '保持自然光线',
        '面部放松，不要化妆',
        '正面拍摄，表情自然',
      ],
    },
    {
      id: 'tongue',
      title: '舌象观察',
      icon: 'food-apple',
      description: '观察舌质、舌苔',
      tips: [
        '张开嘴巴，舌头自然伸出',
        '光线充足，避免阴影',
        '拍摄前不要进食有色食物',
      ],
    },
    {
      id: 'eyes',
      title: '目诊观察',
      icon: 'eye',
      description: '观察眼神、眼周',
      tips: [
        '睁大眼睛，目视前方',
        '确保眼部清晰可见',
        '避免强光直射眼睛',
      ],
    },
  ];

  useEffect(() => {
    Animated.timing(progress, {
      toValue: (currentStep + 1) / steps.length,
      duration: 500,
      useNativeDriver: false,
    }).start();
  }, [currentStep]);

  const handleCapture = async () => {
    setIsAnalyzing(true);
    
    // 模拟图像分析过程
    setTimeout(() => {
      const mockAnalysis: LookAnalysisData = {
        local_fallback: true,
        complexion: currentStep === 0 ? '面色偏黄，略显疲倦' : 
                    currentStep === 1 ? '舌质淡红，苔薄白' : 
                    '眼神略显疲惫，眼周有轻微浮肿',
        features: currentStep === 0 
          ? ['肤色偏黄', '眼袋明显', '神态疲倦']
          : currentStep === 1
          ? ['舌质淡红', '苔薄白', '舌体适中']
          : ['眼神疲倦', '眼周浮肿', '巩膜略黄'],
        constitution: currentStep === 0 ? '气虚质倾向' : 
                      currentStep === 1 ? '脾虚湿盛' : 
                      '肝郁气滞',
        suggestions: currentStep === 0
          ? ['注意休息，保证睡眠', '适当运动，增强体质', '饮食清淡，避免油腻']
          : currentStep === 1
          ? ['健脾祛湿', '少食生冷', '适当运动']
          : ['疏肝理气', '保持心情舒畅', '规律作息'],
      };

      if (currentStep === 0) {
        setFaceAnalysis(mockAnalysis);
      } else if (currentStep === 1) {
        setTongueAnalysis(mockAnalysis);
      } else {
        setEyeAnalysis(mockAnalysis);
      }

      setIsAnalyzing(false);
    }, 2000);
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // 完成所有步骤
      if (onComplete) {
        onComplete({
          face: faceAnalysis || undefined,
          tongue: tongueAnalysis || undefined,
          eyes: eyeAnalysis || undefined,
        });
      }
    }
  };

  const handleSkipStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else if (onSkip) {
      onSkip();
    } else if (onCancel) {
      onCancel();
    }
  };

  const handleAIConsult = () => {
    setShowAgentChat(true);
  };

  const renderAnalysisResult = () => {
    const analysisData = currentStep === 0 ? faceAnalysis : 
                        currentStep === 1 ? tongueAnalysis : 
                        eyeAnalysis;

    if (!analysisData) return null;

    return (
      <Card style={styles.resultCard}>
        <Card.Content>
          <View style={styles.resultHeader}>
            <Text variant="titleMedium" style={styles.resultTitle}>
              分析结果
            </Text>
            {analysisData.local_fallback && (
              <Badge style={styles.localBadge}>本地分析</Badge>
            )}
          </View>

          <View style={styles.resultSection}>
            <Text variant="titleSmall" style={styles.sectionTitle}>
              基本特征
            </Text>
            <Text>{analysisData.complexion}</Text>
            <View style={styles.featureList}>
              {analysisData.features?.map((feature, index) => (
                <Chip key={index} style={styles.featureChip}>
                  {feature}
                </Chip>
              ))}
            </View>
          </View>

          <Divider style={styles.divider} />

          <View style={styles.resultSection}>
            <Text variant="titleSmall" style={styles.sectionTitle}>
              体质倾向
            </Text>
            <Text>{analysisData.constitution}</Text>
          </View>

          <Divider style={styles.divider} />

          <View style={styles.resultSection}>
            <Text variant="titleSmall" style={styles.sectionTitle}>
              调理建议
            </Text>
            {analysisData.suggestions?.map((suggestion, index) => (
              <View key={index} style={styles.suggestionItem}>
                <Icon name="checkbox-marked-circle" size={16} color={theme.colors.primary} />
                <Text style={styles.suggestionText}>{suggestion}</Text>
              </View>
            ))}
          </View>

          <TouchableOpacity
            style={[styles.consultButton, { backgroundColor: theme.colors.primary }]}
            onPress={handleAIConsult}
          >
            <Icon name="robot" size={20} color="white" />
            <Text style={styles.consultButtonText}>咨询小艾医师</Text>
          </TouchableOpacity>
        </Card.Content>
      </Card>
    );
  };

  const renderCamera = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [imageSource, setImageSource] = useState(null);

    const simulateCapture = () => {
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        handleCapture();
      }, 1500);
    };

    let analysisData = null;

    switch (currentStep) {
      case 0:
        analysisData = faceAnalysis;
        break;
      case 1:
        analysisData = tongueAnalysis;
        break;
      case 2:
        analysisData = eyeAnalysis;
        break;
    }

    if (isLoading) {
      return (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
          <Text style={styles.loadingText}>正在分析图像...</Text>
        </View>
      );
    }

    if (analysisData) {
      const iconNames = ['face-man', 'food-apple', 'eye'];
      const iconName = iconNames[currentStep] || 'camera';
      
      return (
        <View style={styles.captureResult}>
          <View style={styles.captureImagePlaceholder}>
            <Icon name={iconName} size={80} color={theme.colors.primary} />
          </View>
          <Text style={styles.imageCaptured}>图像已采集</Text>
          {analysisData.local_fallback && (
            <Chip icon="information" style={styles.localResultChip}>
              本地分析结果
            </Chip>
          )}
        </View>
      );
    }

    return (
      <View style={styles.capturePrompt}>
        <Icon name="camera" size={50} color={theme.colors.primary} />
        <Text style={styles.captureText}>点击拍照</Text>
      </View>
    );
  };

  if (showAgentChat) {
    return (
      <View style={styles.chatContainer}>
        <View style={styles.chatHeader}>
          <TouchableOpacity onPress={() => setShowAgentChat(false)}>
            <Icon name="arrow-left" size={24} color={theme.colors.onSurface} />
          </TouchableOpacity>
          <Text style={styles.chatTitle}>咨询小艾医师</Text>
        </View>
        <View style={styles.chatContent}>
          <Text style={styles.chatMessage}>
            我刚刚完成了望诊检查，以下是结果：
            {faceAnalysis ? `\n面诊：${faceAnalysis.complexion}` : ''}
            {tongueAnalysis ? `\n舌诊：${tongueAnalysis.complexion}` : ''}
            {eyeAnalysis ? `\n目诊：${eyeAnalysis.complexion}` : ''}
            {'\n\n'}请帮我分析这些结果。
          </Text>
        </View>
      </View>
    );
  }

  const currentStepData = steps[currentStep];
  const hasAnalysis = currentStep === 0 ? faceAnalysis : 
                     currentStep === 1 ? tongueAnalysis : 
                     eyeAnalysis;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <View style={styles.progressContainer}>
          <Animated.View
            style={[
              styles.progressBar,
              {
                width: progress.interpolate({
                  inputRange: [0, 1],
                  outputRange: ['0%', '100%'],
                }),
              },
            ]}
          />
        </View>
        <Text variant="labelSmall" style={styles.stepIndicator}>
          {currentStep + 1} / {steps.length}
        </Text>
      </View>

      <View style={styles.content}>
        <View style={styles.stepHeader}>
          <Icon name={currentStepData.icon} size={40} color={theme.colors.primary} />
          <Text variant="headlineSmall" style={styles.stepTitle}>
            {currentStepData.title}
          </Text>
          <Text variant="bodyMedium" style={styles.stepDescription}>
            {currentStepData.description}
          </Text>
        </View>

        <Card style={styles.tipsCard}>
          <Card.Content>
            <Text variant="titleSmall" style={styles.tipsTitle}>
              拍摄提示
            </Text>
            {currentStepData.tips.map((tip, index) => (
              <View key={index} style={styles.tipItem}>
                <Icon name="information" size={16} color={theme.colors.primary} />
                <Text style={styles.tipText}>{tip}</Text>
              </View>
            ))}
          </Card.Content>
        </Card>

        <TouchableOpacity
          style={styles.cameraArea}
          onPress={() => {
            if (!hasAnalysis && !isAnalyzing) {
              handleCapture();
            }
          }}
          disabled={!!hasAnalysis || isAnalyzing}
        >
          {renderCamera()}
        </TouchableOpacity>

        {hasAnalysis && renderAnalysisResult()}

        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.button, styles.skipButton]}
            onPress={handleSkipStep}
          >
            <Text style={styles.skipButtonText}>跳过此步</Text>
          </TouchableOpacity>

          {hasAnalysis && (
            <TouchableOpacity
              style={[styles.button, { backgroundColor: theme.colors.primary }]}
              onPress={handleNext}
            >
              <Text style={styles.nextButtonText}>
                {currentStep === steps.length - 1 ? '完成' : '下一步'}
              </Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 16,
    backgroundColor: 'white',
  },
  progressContainer: {
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#2196F3',
  },
  stepIndicator: {
    textAlign: 'center',
    marginTop: 8,
    color: '#666',
  },
  content: {
    padding: 16,
  },
  stepHeader: {
    alignItems: 'center',
    marginBottom: 24,
  },
  stepTitle: {
    marginTop: 8,
    fontWeight: 'bold',
  },
  stepDescription: {
    marginTop: 4,
    color: '#666',
    textAlign: 'center',
  },
  tipsCard: {
    marginBottom: 16,
  },
  tipsTitle: {
    marginBottom: 8,
    fontWeight: '600',
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  tipText: {
    marginLeft: 8,
    flex: 1,
    fontSize: 14,
    color: '#666',
  },
  cameraArea: {
    height: 300,
    backgroundColor: 'white',
    borderRadius: 12,
    overflow: 'hidden',
    marginBottom: 16,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#e0e0e0',
    borderStyle: 'dashed',
  },
  capturePrompt: {
    alignItems: 'center',
  },
  captureText: {
    marginTop: 8,
    color: '#666',
  },
  captureResult: {
    alignItems: 'center',
    padding: 20,
  },
  captureImage: {
    width: 200,
    height: 200,
    borderRadius: 12,
    marginBottom: 16,
  },
  captureImagePlaceholder: {
    width: 200,
    height: 200,
    borderRadius: 12,
    marginBottom: 16,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  imageCaptured: {
    fontSize: 16,
    color: '#4CAF50',
    fontWeight: '600',
  },
  localResultChip: {
    marginTop: 8,
  },
  loadingContainer: {
    alignItems: 'center',
    padding: 40,
  },
  loadingText: {
    marginTop: 16,
    color: '#666',
  },
  resultCard: {
    marginBottom: 16,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  resultTitle: {
    fontWeight: 'bold',
  },
  localBadge: {
    backgroundColor: '#FF9800',
  },
  resultSection: {
    marginBottom: 12,
  },
  sectionTitle: {
    fontWeight: '600',
    marginBottom: 8,
    color: '#333',
  },
  featureList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
  },
  featureChip: {
    marginRight: 8,
    marginBottom: 8,
  },
  divider: {
    marginVertical: 12,
  },
  suggestionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  suggestionText: {
    marginLeft: 8,
    flex: 1,
  },
  consultButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderRadius: 8,
    marginTop: 16,
  },
  consultButtonText: {
    color: 'white',
    marginLeft: 8,
    fontWeight: '600',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 24,
  },
  button: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    minWidth: 100,
    alignItems: 'center',
  },
  skipButton: {
    backgroundColor: '#e0e0e0',
  },
  skipButtonText: {
    color: '#666',
    fontWeight: '600',
  },
  nextButtonText: {
    color: 'white',
    fontWeight: '600',
  },
  chatContainer: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  chatHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  chatTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 16,
  },
  chatContent: {
    flex: 1,
    padding: 16,
  },
  chatMessage: {
    fontSize: 16,
    lineHeight: 24,
    color: '#333',
  },
});

export default LookDiagnosis;