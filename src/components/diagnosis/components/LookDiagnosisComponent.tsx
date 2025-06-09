import React, { useCallback, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import {
  ImagePickerResponse,
  launchImageLibrary,
} from 'react-native-image-picker';
import { colors, spacing } from '../../../constants/theme';
import {
  DiagnosisComponentProps,
  LookDiagnosisData,
} from '../../../types/diagnosis';

export const LookDiagnosisComponent: React.FC<DiagnosisComponentProps> = ({
  onComplete,
  onCancel,
}) => {
  const [faceImage, setFaceImage] = useState<string | null>(null);
  const [tongueImage, setTongueImage] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const selectImage = useCallback(type: 'face' | 'tongue') => {
    const options = {
      mediaType: 'photo' as const,
      quality: 0.8,
      maxWidth: 1024,
      maxHeight: 1024,
    };

    launchImageLibrary(options, (response: ImagePickerResponse) => {
      if (response.didCancel || response.errorMessage) {
        return;
      }

      if (response.assets && response.assets[0]) {
        const imageUri = response.assets[0].uri;
        if (type === 'face') {
          setFaceImage(imageUri || null);
        } else {
          setTongueImage(imageUri || null);
        }
      }
    });
  }, []);

  const analyzeImages = useCallback(async () => {
    if (!faceImage && !tongueImage) {
      Alert.alert('提示', '请至少上传一张图片进行分析');
      return;
    }

    setIsAnalyzing(true);
    try {
      // 模拟图像分析过程
      await new Promise(resolve) => setTimeout(resolve, 2000));

      const mockResult = {
        faceAnalysis: faceImage;
          ? {
              complexion: '面色红润',
              spirit: '精神饱满',
              features: ['气色良好', '五官端正'],
              confidence: 0.85,
            }
          : null,
        tongueAnalysis: tongueImage;
          ? {
              tongueBody: '舌质淡红',
              tongueCoating: '苔薄白',
              features: ['舌体适中', '舌苔正常'],
              confidence: 0.82,
            }
          : null,
        overallAssessment: '望诊结果显示整体健康状况良好',
        recommendations: ['保持良好的作息习惯', '注意饮食均衡', '适当运动锻炼'],
      };

      setAnalysisResult(mockResult);
    } catch (error) {
      Alert.alert('错误', '图像分析失败，请重试');
    } finally {
      setIsAnalyzing(false);
    }
  }, [faceImage, tongueImage]);

  const handleComplete = useCallback() => {
    const data: LookDiagnosisData = {
      faceImage,
      tongueImage,
      metadata: {
        analysisResult,
        timestamp: new Date().toISOString(),
      },
    };
    onComplete(data);
  }, [faceImage, tongueImage, analysisResult, onComplete]);

  const renderImageSection = (
    title: string,
    image: string | null,
    onPress: () => void,
    description: string;
  ) => (
    <View style={styles.imageSection}>
      <Text style={styles.sectionTitle}>{title}</Text>
      <Text style={styles.sectionDescription}>{description}</Text>

      <TouchableOpacity style={styles.imageContainer} onPress={onPress}>
        {image ? (
          <Image source={ uri: image }} style={styles.image} />
        ) : (
          <View style={styles.imagePlaceholder}>
            <Text style={styles.placeholderText}>点击上传图片</Text>
          </View>
        )}
      </TouchableOpacity>
    </View>
  );

  const renderAnalysisResult = () => {
    if (!analysisResult) return null;

    return (
      <View style={styles.resultContainer}>
        <Text style={styles.resultTitle}>分析结果</Text>

        {analysisResult.faceAnalysis && (
          <View style={styles.analysisSection}>
            <Text style={styles.analysisTitle}>面部分析</Text>
            <Text style={styles.analysisText}>
              面色：{analysisResult.faceAnalysis.complexion}
            </Text>
            <Text style={styles.analysisText}>
              精神：{analysisResult.faceAnalysis.spirit}
            </Text>
            <Text style={styles.confidenceText}>
              置信度：
              {(analysisResult.faceAnalysis.confidence * 100).toFixed(1)}%
            </Text>
          </View>
        )}

        {analysisResult.tongueAnalysis && (
          <View style={styles.analysisSection}>
            <Text style={styles.analysisTitle}>舌象分析</Text>
            <Text style={styles.analysisText}>
              舌质：{analysisResult.tongueAnalysis.tongueBody}
            </Text>
            <Text style={styles.analysisText}>
              舌苔：{analysisResult.tongueAnalysis.tongueCoating}
            </Text>
            <Text style={styles.confidenceText}>
              置信度：
              {(analysisResult.tongueAnalysis.confidence * 100).toFixed(1)}%
            </Text>
          </View>
        )}

        <View style={styles.recommendationSection}>
          <Text style={styles.analysisTitle}>建议</Text>
          {analysisResult.recommendations.map(rec: string, index: number) => (
            <Text key={index} style={styles.recommendationText}>
              • {rec}
            </Text>
          ))}
        </View>
      </View>
    );
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <Text style={styles.title}>望诊分析</Text>
      <Text style={styles.subtitle}>
        通过观察面色、舌象等外在表现，分析身体健康状况
      </Text>

      {renderImageSection(
        '面部图像',
        faceImage,
        () => selectImage('face'),
        '请上传清晰的面部正面照片，确保光线充足'
      )}

      {renderImageSection(
        '舌象图像',
        tongueImage,
        () => selectImage('tongue'),
        '请伸出舌头，拍摄清晰的舌部照片'
      )}

      <View style={styles.actionContainer}>
        <TouchableOpacity;
          style={[styles.button, styles.analyzeButton]}
          onPress={analyzeImages}
          disabled={isAnalyzing || (!faceImage && !tongueImage)}
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
            <Text style={styles.buttonText}>完成望诊</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1,
    padding: spacing.md,
  },
  title: {,
  fontSize: 20,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  subtitle: {,
  fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
    lineHeight: 20,
  },
  imageSection: {,
  marginBottom: spacing.lg,
  },
  sectionTitle: {,
  fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  sectionDescription: {,
  fontSize: 12,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  imageContainer: {,
  borderRadius: 8,
    overflow: 'hidden',
    borderWidth: 2,
    borderColor: colors.border,
    borderStyle: 'dashed',
  },
  image: {,
  width: '100%',
    height: 200,
    resizeMode: 'cover',
  },
  imagePlaceholder: {,
  width: '100%',
    height: 200,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.surface,
  },
  placeholderText: {,
  fontSize: 14,
    color: colors.textSecondary,
  },
  actionContainer: {,
  marginVertical: spacing.md,
  },
  button: {,
  paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: 8,
    alignItems: 'center',
  },
  analyzeButton: {,
  backgroundColor: colors.primary,
  },
  completeButton: {,
  backgroundColor: colors.success,
  },
  buttonText: {,
  fontSize: 16,
    fontWeight: '600',
    color: colors.white,
  },
  resultContainer: {,
  backgroundColor: colors.surface,
    borderRadius: 8,
    padding: spacing.md,
    marginTop: spacing.md,
  },
  resultTitle: {,
  fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  analysisSection: {,
  marginBottom: spacing.md,
    paddingBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  analysisTitle: {,
  fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  analysisText: {,
  fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  confidenceText: {,
  fontSize: 12,
    color: colors.primary,
    fontWeight: '500',
  },
  recommendationSection: {,
  marginTop: spacing.sm,
  },
  recommendationText: {,
  fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    lineHeight: 20,
  },
});
