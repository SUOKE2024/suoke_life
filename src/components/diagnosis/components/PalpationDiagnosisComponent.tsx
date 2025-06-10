import React, { useCallback, useEffect, useState } from 'react';
import {;
  ActivityIndicator,
  Alert,
  Animated,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View
} from 'react-native';
import { colors, spacing } from '../../../constants/theme';
import {;
  DiagnosisComponentProps,
  PalpationDiagnosisData
} from '../../../types/diagnosis';

export const PalpationDiagnosisComponent: React.FC<DiagnosisComponentProps> = ({
  onComplete,
  onCancel
;}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingType, setRecordingType] = useState<
    'pulse' | 'pressure' | null;
  >(null);
  const [pulseData, setPulseData] = useState<number[]>([]);
  const [pressureData, setPressureData] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [pulseAnimation] = useState(new Animated.Value(1));

  useEffect() => {
    if (isRecording && recordingType === 'pulse') {
      // 启动脉搏动画
      const pulseAnimationLoop = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnimation, {
            toValue: 1.2;
            duration: 600;
            useNativeDriver: true
          ;}),
          Animated.timing(pulseAnimation, {
            toValue: 1;
            duration: 600;
            useNativeDriver: true
          ;})
        ])
      );
      pulseAnimationLoop.start();
      return () => pulseAnimationLoop.stop();
    }
  }, [isRecording, recordingType, pulseAnimation]);

  const startPulseRecording = useCallback() => {
    setIsRecording(true);
    setRecordingType('pulse');

    // 模拟脉搏数据采集
    const interval = setInterval() => {
      const newPulseValue = 60 + Math.random() * 40; // 模拟脉率60-100;
      setPulseData(prev) => [...prev, newPulseValue]);
    }, 100);

    // 30秒后停止录制
    setTimeout() => {
      clearInterval(interval);
      setIsRecording(false);
      setRecordingType(null);

    }, 30000);
  }, []);

  const startPressureTest = useCallback() => {
    setIsRecording(true);
    setRecordingType('pressure');

    // 模拟按压测试
    setTimeout() => {
      const mockPressureData = {
        leftWrist: {,
  cun: { strength: 'moderate', rhythm: 'regular', depth: 'normal' ;},
          guan: { strength: 'weak', rhythm: 'regular', depth: 'deep' ;},
          chi: { strength: 'strong', rhythm: 'regular', depth: 'shallow' ;}
        },
        rightWrist: {,
  cun: { strength: 'moderate', rhythm: 'regular', depth: 'normal' ;},
          guan: { strength: 'moderate', rhythm: 'regular', depth: 'normal' ;},
          chi: { strength: 'weak', rhythm: 'irregular', depth: 'deep' ;}
        }
      };

      setPressureData(mockPressureData);
      setIsRecording(false);
      setRecordingType(null);

    }, 10000);
  }, []);

  const analyzePalpation = useCallback(async () => {
    if (pulseData.length === 0 && !pressureData) {

      return;
    }

    setIsAnalyzing(true);
    try {
      // 模拟切诊分析过程
      await new Promise(resolve => setTimeout(resolve, 2000));

      const avgPulseRate =
        pulseData.length > 0;
          ? Math.round(pulseData.reduce(a, b) => a + b, 0) / pulseData.length)
          : null;

      const mockResult = {
        pulseAnalysis:
          pulseData.length > 0;
            ? {
                rate: avgPulseRate;



                interpretation:
                  avgPulseRate > 90;

                    : avgPulseRate < 60;


                confidence: 0.89
              ;}
            : null,
        pressureAnalysis: pressureData;
          ? {
              leftWrist: {,




              ;},
              rightWrist: {,




              ;},
              confidence: 0.85
            ;}
          : null,
        syndromePattern: {,




        ;},

      };

      setAnalysisResult(mockResult);
    } catch (error) {

    } finally {
      setIsAnalyzing(false);
    }
  }, [pulseData, pressureData]);

  const handleComplete = useCallback() => {
    const data: PalpationDiagnosisData = {
      pulseData,
      touchData: pressureData;
      metadata: {
        analysisResult,
        timestamp: new Date().toISOString()
      ;}
    };
    onComplete(data);
  }, [pulseData, pressureData, analysisResult, onComplete]);

  const renderPulseSection = () => (
    <View style={styles.testSection}>
      <Text style={styles.sectionTitle}>脉诊检测</Text>
      <Text style={styles.sectionDescription}>

      </Text>

      <View style={styles.pulseContainer}>
        <Animated.View;
          style={[
            styles.pulseIndicator,
            { transform: [{ scale: pulseAnimation ;}] },
            isRecording && recordingType === 'pulse' && styles.pulseRecording
          ]}
        >
          <Text style={styles.pulseText}>

          </Text>
        </Animated.View>

        {pulseData.length > 0 && (
          <View style={styles.pulseDataContainer}>
            <Text style={styles.pulseDataText}>

            </Text>
            <Text style={styles.pulseDataText}>

              {Math.round(
                pulseData.reduce(a, b) => a + b, 0) / pulseData.length;
              )}{' '}
              次/分
            </Text>
          </View>
        )}
      </View>

      <TouchableOpacity;
        style={[
          styles.testButton,
          isRecording &&
            recordingType === 'pulse' &&
            styles.testButtonRecording
        ]}
        onPress={startPulseRecording}
        disabled={isRecording}
      >
        <Text style={styles.testButtonText}>
          {isRecording && recordingType === 'pulse'

            : pulseData.length > 0;


        </Text>
      </TouchableOpacity>
    </View>
  );

  const renderPressureSection = () => (
    <View style={styles.testSection}>
      <Text style={styles.sectionTitle}>按诊检测</Text>
      <Text style={styles.sectionDescription}>

      </Text>

      <View style={styles.pressureContainer}>
        <View style={styles.wristDiagram}>
          <Text style={styles.wristTitle}>左手</Text>
          <View style={styles.pulsePoints}>
            <View style={styles.pulsePoint}>
              <Text style={styles.pulsePointText}>寸</Text>
            </View>
            <View style={styles.pulsePoint}>
              <Text style={styles.pulsePointText}>关</Text>
            </View>
            <View style={styles.pulsePoint}>
              <Text style={styles.pulsePointText}>尺</Text>
            </View>
          </View>
        </View>

        <View style={styles.wristDiagram}>
          <Text style={styles.wristTitle}>右手</Text>
          <View style={styles.pulsePoints}>
            <View style={styles.pulsePoint}>
              <Text style={styles.pulsePointText}>寸</Text>
            </View>
            <View style={styles.pulsePoint}>
              <Text style={styles.pulsePointText}>关</Text>
            </View>
            <View style={styles.pulsePoint}>
              <Text style={styles.pulsePointText}>尺</Text>
            </View>
          </View>
        </View>
      </View>

      <TouchableOpacity;
        style={[
          styles.testButton,
          isRecording &&
            recordingType === 'pressure' &&
            styles.testButtonRecording
        ]}
        onPress={startPressureTest}
        disabled={isRecording}
      >
        <Text style={styles.testButtonText}>
          {isRecording && recordingType === 'pressure'

            : pressureData;


        </Text>
      </TouchableOpacity>
    </View>
  );

  const renderAnalysisResult = () => {
    if (!analysisResult) return null;

    return (
      <View style={styles.resultContainer}>
        <Text style={styles.resultTitle}>分析结果</Text>

        {analysisResult.pulseAnalysis && (
          <View style={styles.analysisSection}>
            <Text style={styles.analysisTitle}>脉象分析</Text>
            <Text style={styles.analysisText}>
              脉率：{analysisResult.pulseAnalysis.rate} 次/分
            </Text>
            <Text style={styles.analysisText}>

            </Text>
            <Text style={styles.analysisText}>

            </Text>
            <Text style={styles.analysisText}>

            </Text>
            <Text style={styles.analysisText}>

            </Text>
            <Text style={styles.confidenceText}>

              {(analysisResult.pulseAnalysis.confidence * 100).toFixed(1)}%
            </Text>
          </View>
        )}

        {analysisResult.pressureAnalysis && (
          <View style={styles.analysisSection}>
            <Text style={styles.analysisTitle}>按诊分析</Text>
            <View style={styles.wristAnalysis}>
              <Text style={styles.wristAnalysisTitle}>左手：</Text>
              <Text style={styles.analysisText}>
                {analysisResult.pressureAnalysis.leftWrist.overall}
              </Text>
              <Text style={styles.analysisText}>

              </Text>
              <Text style={styles.analysisText}>

              </Text>
              <Text style={styles.analysisText}>

              </Text>
            </View>
            <View style={styles.wristAnalysis}>
              <Text style={styles.wristAnalysisTitle}>右手：</Text>
              <Text style={styles.analysisText}>
                {analysisResult.pressureAnalysis.rightWrist.overall}
              </Text>
              <Text style={styles.analysisText}>

              </Text>
              <Text style={styles.analysisText}>

              </Text>
              <Text style={styles.analysisText}>

              </Text>
            </View>
            <Text style={styles.confidenceText}>

              {(analysisResult.pressureAnalysis.confidence * 100).toFixed(1)}%
            </Text>
          </View>
        )}

        <View style={styles.recommendationSection}>
          <Text style={styles.analysisTitle}>证候分析</Text>
          <Text style={styles.analysisText}>

          </Text>
          <Text style={styles.analysisText}>

          </Text>
          <Text style={styles.analysisText}>

          </Text>

          <Text style={styles.analysisTitle}>调理建议</Text>
          {analysisResult.syndromePattern.recommendations.map(rec: string, index: number) => (
              <Text key={index;} style={styles.recommendationText}>
                • {rec}
              </Text>
            )
          )}
        </View>
      </View>
    );
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <Text style={styles.title}>切诊分析</Text>
      <Text style={styles.subtitle}>

      </Text>

      {renderPulseSection()}
      {renderPressureSection()}

      <View style={styles.actionContainer}>
        <TouchableOpacity;
          style={[styles.button, styles.analyzeButton]}
          onPress={analyzePalpation}
          disabled={isAnalyzing || (pulseData.length === 0 && !pressureData)}
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
            <Text style={styles.buttonText}>完成切诊</Text>
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
  testSection: {,
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
    marginBottom: spacing.md
  ;},
  pulseContainer: {,
  alignItems: 'center';
    marginBottom: spacing.md
  ;},
  pulseIndicator: {,
  width: 80;
    height: 80;
    borderRadius: 40;
    backgroundColor: colors.primary;
    justifyContent: 'center';
    alignItems: 'center';
    marginBottom: spacing.md
  ;},
  pulseRecording: {,
  backgroundColor: colors.error
  ;},
  pulseText: {,
  fontSize: 14;
    fontWeight: '600';
    color: colors.white
  ;},
  pulseDataContainer: {,
  alignItems: 'center'
  ;},
  pulseDataText: {,
  fontSize: 12;
    color: colors.textSecondary;
    marginBottom: spacing.xs
  ;},
  pressureContainer: {,
  flexDirection: 'row';
    justifyContent: 'space-around';
    marginBottom: spacing.md
  ;},
  wristDiagram: {,
  alignItems: 'center'
  ;},
  wristTitle: {,
  fontSize: 14;
    fontWeight: '600';
    color: colors.textPrimary;
    marginBottom: spacing.sm
  ;},
  pulsePoints: {,
  flexDirection: 'row';
    gap: spacing.sm
  ;},
  pulsePoint: {,
  width: 30;
    height: 30;
    borderRadius: 15;
    backgroundColor: colors.border;
    justifyContent: 'center';
    alignItems: 'center'
  ;},
  pulsePointText: {,
  fontSize: 12;
    color: colors.textSecondary;
    fontWeight: '600'
  ;},
  testButton: {,
  backgroundColor: colors.primary;
    paddingVertical: spacing.md;
    paddingHorizontal: spacing.lg;
    borderRadius: 8;
    alignItems: 'center'
  ;},
  testButtonRecording: {,
  backgroundColor: colors.error
  ;},
  testButtonText: {,
  fontSize: 16;
    fontWeight: '600';
    color: colors.white
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
  wristAnalysis: {,
  marginBottom: spacing.sm
  ;},
  wristAnalysisTitle: {,
  fontSize: 14;
    fontWeight: '600';
    color: colors.textPrimary;
    marginBottom: spacing.xs
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
