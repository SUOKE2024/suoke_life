import React, { useCallback, useState } from 'react';
import {;
  ActivityIndicator,
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View
} from 'react-native';
import { colors, spacing } from '../../../constants/theme';
import {;
  DiagnosisComponentProps,
  ListenDiagnosisData
} from '../../../types/diagnosis';

export const ListenDiagnosisComponent: React.FC<DiagnosisComponentProps> = ({
  onComplete,
  onCancel
;}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingType, setRecordingType] = useState<
    'voice' | 'breathing' | 'cough' | null;
  >(null);
  const [recordings, setRecordings] = useState<{
    voice?: string;
    breathing?: string;
    cough?: string;
  }>({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const startRecording = useCallback(type: 'voice' | 'breathing' | 'cough') => {
      setIsRecording(true);
      setRecordingType(type);

      // 模拟录音过程
      setTimeout() => {
        setIsRecording(false);
        setRecordings(prev) => ({
          ...prev,
          [type]: `recording_${type}_${Date.now()}.wav`
        }));
        setRecordingType(null);

      }, 3000);
    },
    []
  );

  const getRecordingTypeLabel = (type: 'voice' | 'breathing' | 'cough') => {
    switch (type) {
      case 'voice':

      case 'breathing':

      case 'cough':

      default:
        return '';
    }
  };

  const analyzeRecordings = useCallback(async () => {
    if (Object.keys(recordings).length === 0) {

      return;
    }

    setIsAnalyzing(true);
    try {
      // 模拟音频分析过程
      await new Promise(resolve => setTimeout(resolve, 2000));

      const mockResult = {
        voiceAnalysis: recordings.voice;
          ? {




              confidence: 0.88
            ;}
          : null,
        breathingAnalysis: recordings.breathing;
          ? {




              confidence: 0.85
            ;}
          : null,
        coughAnalysis: recordings.cough;
          ? {




              confidence: 0.82
            ;}
          : null,

        recommendations: [



        ]
      ;};

      setAnalysisResult(mockResult);
    } catch (error) {

    } finally {
      setIsAnalyzing(false);
    }
  }, [recordings]);

  const handleComplete = useCallback() => {
    const data: ListenDiagnosisData = {,
  voiceRecording: recordings.voice;
      breathingPattern: recordings.breathing;
      coughSound: recordings.cough;
      metadata: {
        analysisResult,
        timestamp: new Date().toISOString()
      ;}
    };
    onComplete(data);
  }, [recordings, analysisResult, onComplete]);

  const renderRecordingSection = (
    type: 'voice' | 'breathing' | 'cough';
    title: string;
    description: string;
    instruction: string;
  ) => (
    <View style={styles.recordingSection}>
      <Text style={styles.sectionTitle}>{title}</Text>
      <Text style={styles.sectionDescription}>{description}</Text>
      <Text style={styles.instructionText}>{instruction}</Text>

      <View style={styles.recordingContainer}>
        {recordings[type] ? (
          <View style={styles.recordedIndicator}>
            <Text style={styles.recordedText}>✓ 已录制</Text>
            <TouchableOpacity;
              style={styles.reRecordButton}
              onPress={() => startRecording(type)}
              disabled={isRecording}
            >
              <Text style={styles.reRecordText}>重新录制</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <TouchableOpacity;
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
            <Text style={styles.analysisText}>

            </Text>
            <Text style={styles.analysisText}>

            </Text>
            <Text style={styles.analysisText}>

            </Text>
            <Text style={styles.confidenceText}>

              {(analysisResult.voiceAnalysis.confidence * 100).toFixed(1)}%
            </Text>
          </View>
        )}

        {analysisResult.breathingAnalysis && (
          <View style={styles.analysisSection}>
            <Text style={styles.analysisTitle}>呼吸音分析</Text>
            <Text style={styles.analysisText}>

            </Text>
            <Text style={styles.analysisText}>

            </Text>
            <Text style={styles.analysisText}>

            </Text>
            <Text style={styles.confidenceText}>

              {(analysisResult.breathingAnalysis.confidence * 100).toFixed(1)}%
            </Text>
          </View>
        )}

        {analysisResult.coughAnalysis && (
          <View style={styles.analysisSection}>
            <Text style={styles.analysisTitle}>咳嗽音分析</Text>
            <Text style={styles.analysisText}>

            </Text>
            <Text style={styles.analysisText}>

            </Text>
            <Text style={styles.analysisText}>

            </Text>
            <Text style={styles.confidenceText}>

              {(analysisResult.coughAnalysis.confidence * 100).toFixed(1)}%
            </Text>
          </View>
        )}

        <View style={styles.recommendationSection}>
          <Text style={styles.analysisTitle}>建议</Text>
          {analysisResult.recommendations.map(rec: string, index: number) => (
            <Text key={index;} style={styles.recommendationText}>
              • {rec}
            </Text>
          ))}
        </View>
      </View>
    );
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <Text style={styles.title}>闻诊分析</Text>
      <Text style={styles.subtitle}>

      </Text>

      {renderRecordingSection(
        'voice',



      )}

      {renderRecordingSection(
        'breathing',



      )}

      {renderRecordingSection(
        'cough',



      )}

      <View style={styles.actionContainer}>
        <TouchableOpacity;
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
          <TouchableOpacity;
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
  container: {,
  flex: 1;
    padding: spacing.md
  ;},
  title: {,
  fontSize: 20;
    fontWeight: '600';
    color: colors.textPrimary;
    marginBottom: spacing.sm
  ;},
  subtitle: {,
  fontSize: 14;
    color: colors.textSecondary;
    marginBottom: spacing.lg;
    lineHeight: 20
  ;},
  recordingSection: {,
  marginBottom: spacing.lg;
    backgroundColor: colors.surface;
    borderRadius: 8;
    padding: spacing.md
  ;},
  sectionTitle: {,
  fontSize: 16;
    fontWeight: '600';
    color: colors.textPrimary;
    marginBottom: spacing.xs
  ;},
  sectionDescription: {,
  fontSize: 14;
    color: colors.textSecondary;
    marginBottom: spacing.sm
  ;},
  instructionText: {,
  fontSize: 12;
    color: colors.textTertiary;
    marginBottom: spacing.md;
    fontStyle: 'italic'
  ;},
  recordingContainer: {,
  alignItems: 'center'
  ;},
  recordButton: {,
  backgroundColor: colors.primary;
    paddingVertical: spacing.md;
    paddingHorizontal: spacing.lg;
    borderRadius: 8;
    minWidth: 120;
    alignItems: 'center'
  ;},
  recordingButton: {,
  backgroundColor: colors.error
  ;},
  recordButtonText: {,
  fontSize: 16;
    fontWeight: '600';
    color: colors.white
  ;},
  recordingIndicator: {,
  flexDirection: 'row';
    alignItems: 'center';
    gap: spacing.sm
  ;},
  recordingText: {,
  fontSize: 16;
    fontWeight: '600';
    color: colors.white
  ;},
  recordedIndicator: {,
  flexDirection: 'row';
    alignItems: 'center';
    gap: spacing.md
  ;},
  recordedText: {,
  fontSize: 16;
    color: colors.success;
    fontWeight: '600'
  ;},
  reRecordButton: {,
  backgroundColor: colors.border;
    paddingVertical: spacing.sm;
    paddingHorizontal: spacing.md;
    borderRadius: 6
  ;},
  reRecordText: {,
  fontSize: 14;
    color: colors.textSecondary
  ;},
  actionContainer: {,
  marginVertical: spacing.md
  ;},
  button: {,
  paddingVertical: spacing.md;
    paddingHorizontal: spacing.lg;
    borderRadius: 8;
    alignItems: 'center'
  ;},
  analyzeButton: {,
  backgroundColor: colors.primary
  ;},
  completeButton: {,
  backgroundColor: colors.success
  ;},
  buttonText: {,
  fontSize: 16;
    fontWeight: '600';
    color: colors.white
  ;},
  resultContainer: {,
  backgroundColor: colors.surface;
    borderRadius: 8;
    padding: spacing.md;
    marginTop: spacing.md
  ;},
  resultTitle: {,
  fontSize: 18;
    fontWeight: '600';
    color: colors.textPrimary;
    marginBottom: spacing.md
  ;},
  analysisSection: {,
  marginBottom: spacing.md;
    paddingBottom: spacing.md;
    borderBottomWidth: 1;
    borderBottomColor: colors.border
  ;},
  analysisTitle: {,
  fontSize: 16;
    fontWeight: '600';
    color: colors.textPrimary;
    marginBottom: spacing.sm
  ;},
  analysisText: {,
  fontSize: 14;
    color: colors.textSecondary;
    marginBottom: spacing.xs
  ;},
  confidenceText: {,
  fontSize: 12;
    color: colors.primary;
    fontWeight: '500'
  ;},
  recommendationSection: {,
  marginTop: spacing.sm
  ;},
  recommendationText: {,
  fontSize: 14;
    color: colors.textSecondary;
    marginBottom: spacing.xs;
    lineHeight: 20
  ;}
});
