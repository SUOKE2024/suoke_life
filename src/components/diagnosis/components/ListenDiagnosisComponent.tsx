import React, { useCallback, useState } from 'react';
import {
    ActivityIndicator,
    Alert,
    ScrollView,
    StyleSheet,
    Text,
    TouchableOpacity,
    View,
} from 'react-native';
import { colors, spacing } from '../../../constants/theme';
import { DiagnosisComponentProps, ListenDiagnosisData } from '../../../types/diagnosis';

export const ListenDiagnosisComponent: React.FC<DiagnosisComponentProps> = ({
  onComplete,
  onCancel,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingType, setRecordingType] = useState<'voice' | 'breathing' | 'cough' | null>(null);
  const [recordings, setRecordings] = useState<{
    voice?: string;
    breathing?: string;
    cough?: string;
  }>({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const startRecording = useCallback((type: 'voice' | 'breathing' | 'cough') => {
    setIsRecording(true);
    setRecordingType(type);
    
    // 模拟录音过程
    setTimeout(() => {
      setIsRecording(false);
      setRecordings(prev => ({
        ...prev,
        [type]: `recording_${type}_${Date.now()}.wav`
      }));
      setRecordingType(null);
      Alert.alert('录音完成', `${getRecordingTypeLabel(type)}录音已保存`);
    }, 3000);
  }, []);

  const getRecordingTypeLabel = (type: 'voice' | 'breathing' | 'cough') => {
    switch (type) {
      case 'voice': return '语音';
      case 'breathing': return '呼吸音';
      case 'cough': return '咳嗽音';
      default: return '';
    }
  };

  const analyzeRecordings = useCallback(async () => {
    if (Object.keys(recordings).length === 0) {
      Alert.alert('提示', '请至少录制一段音频进行分析');
      return;
    }

    setIsAnalyzing(true);
    try {
      // 模拟音频分析过程
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockResult = {
        voiceAnalysis: recordings.voice ? {
          tone: '声音洪亮',
          rhythm: '语速适中',
          quality: '音质清晰',
          features: ['声音有力', '语调平稳'],
          confidence: 0.88,
        } : null,
        breathingAnalysis: recordings.breathing ? {
          pattern: '呼吸平稳',
          depth: '深度适中',
          frequency: '频率正常',
          features: ['呼吸顺畅', '无异常音'],
          confidence: 0.85,
        } : null,
        coughAnalysis: recordings.cough ? {
          type: '干咳',
          intensity: '轻微',
          frequency: '偶发',
          features: ['咳嗽清浅', '无痰音'],
          confidence: 0.82,
        } : null,
        overallAssessment: '闻诊结果显示呼吸系统功能正常',
        recommendations: [
          '保持室内空气流通',
          '避免接触刺激性气味',
          '适当进行呼吸锻炼',
        ],
      };

      setAnalysisResult(mockResult);
    } catch (error) {
      Alert.alert('错误', '音频分析失败，请重试');
    } finally {
      setIsAnalyzing(false);
    }
  }, [recordings]);

  const handleComplete = useCallback(() => {
    const data: ListenDiagnosisData = {
      voiceRecording: recordings.voice,
      breathingPattern: recordings.breathing,
      coughSound: recordings.cough,
      metadata: {
        analysisResult,
        timestamp: new Date().toISOString(),
      },
    };
    onComplete(data);
  }, [recordings, analysisResult, onComplete]);

  const renderRecordingSection = (
    type: 'voice' | 'breathing' | 'cough',
    title: string,
    description: string,
    instruction: string
  ) => (
    <View style={styles.recordingSection}>
      <Text style={styles.sectionTitle}>{title}</Text>
      <Text style={styles.sectionDescription}>{description}</Text>
      <Text style={styles.instructionText}>{instruction}</Text>
      
      <View style={styles.recordingContainer}>
        {recordings[type] ? (
          <View style={styles.recordedIndicator}>
            <Text style={styles.recordedText}>✓ 已录制</Text>
            <TouchableOpacity
              style={styles.reRecordButton}
              onPress={() => startRecording(type)}
              disabled={isRecording}
            >
              <Text style={styles.reRecordText}>重新录制</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <TouchableOpacity
            style={[
              styles.recordButton,
              isRecording && recordingType === type && styles.recordingButton
            ]}
            onPress={() => startRecording(type)}
            disabled={isRecording}
          >
            {isRecording && recordingType === type ? (
              <View style={styles.recordingIndicator}>
                <ActivityIndicator size="small" color={colors.white} />
                <Text style={styles.recordingText}>录制中...</Text>
              </View>
            ) : (
              <Text style={styles.recordButtonText}>开始录制</Text>
            )}
          </TouchableOpacity>
        )}
      </View>
    </View>
  );

  const renderAnalysisResult = () => {
    if (!analysisResult) return null;

    return (
      <View style={styles.resultContainer}>
        <Text style={styles.resultTitle}>分析结果</Text>
        
        {analysisResult.voiceAnalysis && (
          <View style={styles.analysisSection}>
            <Text style={styles.analysisTitle}>语音分析</Text>
            <Text style={styles.analysisText}>音调：{analysisResult.voiceAnalysis.tone}</Text>
            <Text style={styles.analysisText}>节律：{analysisResult.voiceAnalysis.rhythm}</Text>
            <Text style={styles.analysisText}>音质：{analysisResult.voiceAnalysis.quality}</Text>
            <Text style={styles.confidenceText}>
              置信度：{(analysisResult.voiceAnalysis.confidence * 100).toFixed(1)}%
            </Text>
          </View>
        )}

        {analysisResult.breathingAnalysis && (
          <View style={styles.analysisSection}>
            <Text style={styles.analysisTitle}>呼吸音分析</Text>
            <Text style={styles.analysisText}>模式：{analysisResult.breathingAnalysis.pattern}</Text>
            <Text style={styles.analysisText}>深度：{analysisResult.breathingAnalysis.depth}</Text>
            <Text style={styles.analysisText}>频率：{analysisResult.breathingAnalysis.frequency}</Text>
            <Text style={styles.confidenceText}>
              置信度：{(analysisResult.breathingAnalysis.confidence * 100).toFixed(1)}%
            </Text>
          </View>
        )}

        {analysisResult.coughAnalysis && (
          <View style={styles.analysisSection}>
            <Text style={styles.analysisTitle}>咳嗽音分析</Text>
            <Text style={styles.analysisText}>类型：{analysisResult.coughAnalysis.type}</Text>
            <Text style={styles.analysisText}>强度：{analysisResult.coughAnalysis.intensity}</Text>
            <Text style={styles.analysisText}>频率：{analysisResult.coughAnalysis.frequency}</Text>
            <Text style={styles.confidenceText}>
              置信度：{(analysisResult.coughAnalysis.confidence * 100).toFixed(1)}%
            </Text>
          </View>
        )}

        <View style={styles.recommendationSection}>
          <Text style={styles.analysisTitle}>建议</Text>
          {analysisResult.recommendations.map((rec: string, index: number) => (
            <Text key={index} style={styles.recommendationText}>• {rec}</Text>
          ))}
        </View>
      </View>
    );
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <Text style={styles.title}>闻诊分析</Text>
      <Text style={styles.subtitle}>
        通过听取语音、呼吸音等声音信息，分析身体健康状况
      </Text>

      {renderRecordingSection(
        'voice',
        '语音录制',
        '录制您的正常说话声音',
        '请用正常音量说话30秒，内容可以是自我介绍或朗读'
      )}

      {renderRecordingSection(
        'breathing',
        '呼吸音录制',
        '录制您的呼吸声音',
        '请保持安静，进行正常呼吸，录制时长约30秒'
      )}

      {renderRecordingSection(
        'cough',
        '咳嗽音录制（可选）',
        '如有咳嗽症状，请录制咳嗽声',
        '如果有咳嗽，请自然咳嗽几声进行录制'
      )}

      <View style={styles.actionContainer}>
        <TouchableOpacity
          style={[styles.button, styles.analyzeButton]}
          onPress={analyzeRecordings}
          disabled={isAnalyzing || Object.keys(recordings).length === 0}
        >
          {isAnalyzing ? (
            <ActivityIndicator size="small" color={colors.white} />
          ) : (
            <Text style={styles.buttonText}>开始分析</Text>
          )}
        </TouchableOpacity>
      </View>

      {renderAnalysisResult()}

      {analysisResult && (
        <View style={styles.actionContainer}>
          <TouchableOpacity
            style={[styles.button, styles.completeButton]}
            onPress={handleComplete}
          >
            <Text style={styles.buttonText}>完成闻诊</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: spacing.md,
  },
  title: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
    lineHeight: 20,
  },
  recordingSection: {
    marginBottom: spacing.lg,
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: spacing.md,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  sectionDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  instructionText: {
    fontSize: 12,
    color: colors.textTertiary,
    marginBottom: spacing.md,
    fontStyle: 'italic',
  },
  recordingContainer: {
    alignItems: 'center',
  },
  recordButton: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: 8,
    minWidth: 120,
    alignItems: 'center',
  },
  recordingButton: {
    backgroundColor: colors.error,
  },
  recordButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.white,
  },
  recordingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  recordingText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.white,
  },
  recordedIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
  },
  recordedText: {
    fontSize: 16,
    color: colors.success,
    fontWeight: '600',
  },
  reRecordButton: {
    backgroundColor: colors.border,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: 6,
  },
  reRecordText: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  actionContainer: {
    marginVertical: spacing.md,
  },
  button: {
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: 8,
    alignItems: 'center',
  },
  analyzeButton: {
    backgroundColor: colors.primary,
  },
  completeButton: {
    backgroundColor: colors.success,
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.white,
  },
  resultContainer: {
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: spacing.md,
    marginTop: spacing.md,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  analysisSection: {
    marginBottom: spacing.md,
    paddingBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  analysisTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  analysisText: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  confidenceText: {
    fontSize: 12,
    color: colors.primary,
    fontWeight: '500',
  },
  recommendationSection: {
    marginTop: spacing.sm,
  },
  recommendationText: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    lineHeight: 20,
  },
}); 