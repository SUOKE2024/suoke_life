import { useNavigation } from "@react-navigation/native";""/;,"/g"/;
import React, { useEffect, useRef, useState } from "react";";
import {;,}Alert,;
Animated,;
Dimensions,;
ScrollView,;
StyleSheet,;
Text,;
TouchableOpacity,";"";
}
  View'}'';'';
} from "react-native";";
import { SafeAreaView } from "react-native-safe-area-context";";
import Icon from "react-native-vector-icons/MaterialCommunityIcons";""/;,"/g"/;
import { Button } from "../../components/ui/Button";""/;,"/g"/;
import { ProgressBar } from "../../components/ui/ProgressBar";""/;,"/g"/;
import {;,}borderRadius,;
colors,;
shadows,;
spacing,";"";
}
  typography'}'';'';
} from "../../constants/theme";""/;"/g"/;
';,'';
const { width: screenWidth ;} = Dimensions.get('window');';,'';
interface DiagnosisStep {id: string}title: string,;
description: string,;
icon: string,;
color: string,;
completed: boolean,;
const active = boolean;
}
}
  data?: any;}
}

interface DiagnosisResult {syndrome: string}confidence: number,;
symptoms: string[],;
const recommendations = string[];
}
}
  prescription?: string;}
}

const  EnhancedDiagnosisScreen: React.FC = () => {const navigation = useNavigation();,}const scrollViewRef = useRef<ScrollView>(null);
const [currentStep, setCurrentStep] = useState(0);
const [progress, setProgress] = useState(0);
const [isProcessing, setIsProcessing] = useState(false);
const [diagnosisResult, setDiagnosisResult] =;
useState<DiagnosisResult | null>(null);

  // 动画值/;,/g/;
const fadeAnim = useRef(new Animated.Value(0)).current;
const slideAnim = useRef(new Animated.Value(50)).current;
const scaleAnim = useRef(new Animated.Value(0.8)).current;

  // 四诊步骤/;,/g/;
const [steps, setSteps] = useState<DiagnosisStep[]>([;)';]    {';,}id: 'look';','';'';
';'';
';,'';
icon: 'eye';','';
color: colors.primary,;
completed: false,;
}
      const active = true}
    ;},';'';
    {';,}id: 'listen';','';'';
';'';
';,'';
icon: 'ear-hearing';','';
color: colors.secondary,;
completed: false,;
}
      const active = false}
    ;},';'';
    {';,}id: 'inquiry';','';'';
';'';
';,'';
icon: 'comment-question';','';
color: colors.warning,;
completed: false,;
}
      const active = false}
    ;},';'';
    {';,}id: 'palpation';','';'';
';'';
';,'';
icon: 'hand-back-left';','';
color: colors.info,;
completed: false,);
}
      const active = false)}
    ;});
];
  ]);

  // 初始化动画/;,/g/;
useEffect() => {Animated.parallel([;,)Animated.timing(fadeAnim, {)        toValue: 1,);,]duration: 800,);}}
        const useNativeDriver = true)}
      ;}),;
Animated.timing(slideAnim, {)toValue: 0,);,}duration: 800,);
}
        const useNativeDriver = true)}
      ;}),;
Animated.spring(scaleAnim, {));,}toValue: 1,);
}
        const useNativeDriver = true)}
      ;});
];
    ]).start();
  }, []);

  // 更新进度/;,/g/;
useEffect() => {const completedSteps = steps.filter(step) => step.completed).length;,}const newProgress = (completedSteps / steps.length) * 100;/;/g/;
}
    setProgress(newProgress);}
  }, [steps]);

  // 进入下一步/;,/g/;
const  nextStep = useCallback(() => {if (currentStep < steps.length - 1) {}      // 标记当前步骤为完成/;,/g/;
setSteps(prev) =>;
prev.map(step, index) => ({)          ...step}completed: index === currentStep ? true : step.completed,;
active: ;
index === currentStep + 1;
              ? true;
              : index === currentStep;);
                ? false;);
}
                : step.active)}
        }));
      );
setCurrentStep(prev) => prev + 1);

      // 滚动到下一步/;,/g/;
setTimeout() => {scrollViewRef.current?.scrollTo({);,}y: (currentStep + 1) * 200,;
}
          const animated = true}
        ;});
      }, 300);
    } else {// 完成所有步骤，开始分析/;,}setSteps(prev) =>;,/g/;
prev.map(step, index) => ({)          ...step,);,}completed: index === currentStep ? true : step.completed,);
}
          const active = false)}
        ;}));
      );
startDiagnosisAnalysis();
    }
  };

  // 开始诊断分析/;,/g/;
const  startDiagnosisAnalysis = async () => {setIsProcessing(true);}    // 模拟AI分析过程/;,/g,/;
  await: new Promise(resolve => setTimeout(resolve, 3000));

    // 模拟诊断结果/;,/g,/;
  const: result: DiagnosisResult = {confidence: 85,;
const recommendations = [;]];
      ],;
}
}
    ;};
setDiagnosisResult(result);
setIsProcessing(false);
  };

  // 重新开始/;,/g/;
const  restart = useCallback(() => {setCurrentStep(0);,}setProgress(0);
setIsProcessing(false);
setDiagnosisResult(null);
setSteps(prev) =>;
prev.map(step, index) => ({)        ...step,);,}completed: false,);
}
        active: index === 0)}
      ;}));
    );
  };

  // 渲染步骤卡片/;,/g,/;
  const: renderStepCard = useCallback((step: DiagnosisStep, index: number) => {const isActive = step.active;,}const isCompleted = step.completed;
const isCurrent = index === currentStep;

}
    return (<Animated.View;}  />/;,)key={step.id}/g/;
        style={[;,]styles.stepCard}isActive && styles.activeStepCard,;
isCompleted && styles.completedStepCard,;
          {opacity: fadeAnim,;}}
            const transform = [}]              { translateY: slideAnim ;}
              { scale: isCurrent ? scaleAnim : 1 ;}
];
            ];
          }
        ]}
      >;
        <View style={styles.stepHeader}>;
          <View;  />/;,/g/;
style={}[;]}
              styles.stepIcon,}
              { backgroundColor: step.color ;}
isCompleted && styles.completedStepIcon;
];
            ]}
          >';'';
            <Icon;'  />/;,'/g'/;
name={isCompleted ? 'check' : step.icon}';,'';
size={24}
              color={colors.white}
            />/;/g/;
          </View>/;/g/;
          <View style={styles.stepInfo}>;
            <Text;  />/;,/g/;
style={[styles.stepTitle, isActive && styles.activeStepTitle]}
            >;
              {step.title}
            </Text>/;/g/;
            <Text style={styles.stepDescription}>{step.description}</Text>/;/g/;
          </View>/;/g/;
          <View style={styles.stepStatus}>)';'';
            {isCompleted && ()'}'';'';
              <Icon name="check-circle" size={20} color={colors.success}  />")""/;"/g"/;
            )}
            {isActive && !isCompleted && (<View style={styles.activeIndicator}  />)/;/g/;
            )}
          </View>/;/g/;
        </View>/;/g/;

        {isCurrent && !isCompleted && ()}
          <View style={styles.stepContent}>{renderStepContent(step)}</View>/;/g/;
        )}
      </Animated.View>/;/g/;
    );
  };

  // 渲染步骤内容/;,/g/;
const  renderStepContent = useCallback((step: DiagnosisStep) => {";,}switch (step.id) {";}}"";
      case 'look':'}'';
return (<View style={styles.contentContainer;}>;)            <Text style={styles.contentTitle}>请上传面部照片和舌象照片</Text>/;/g/;
            <View style={styles.uploadContainer}>';'';
              <TouchableOpacity style={styles.uploadButton}>';'';
                <Icon name="camera" size={32} color={colors.primary}  />"/;"/g"/;
                <Text style={styles.uploadText}>拍摄面部照片</Text>/;/g/;
              </TouchableOpacity>"/;"/g"/;
              <TouchableOpacity style={styles.uploadButton}>";"";
                <Icon name="camera" size={32} color={colors.primary}  />"/;"/g"/;
                <Text style={styles.uploadText}>拍摄舌象照片</Text>/;/g/;
              </TouchableOpacity>/;/g/;
            </View>/;/g/;
            <Button;  />/;,/g/;
onPress={nextStep}
              style={styles.nextButton});
            />)/;/g/;
          </View>)/;/g/;
        );";"";
";,"";
case 'listen': ';,'';
return (<View style={styles.contentContainer}>;)            <Text style={styles.contentTitle}>请录制语音样本</Text>/;/g/;
            <View style={styles.recordContainer}>';'';
              <TouchableOpacity style={styles.recordButton}>';'';
                <Icon name="microphone" size={48} color={colors.secondary}  />"/;"/g"/;
                <Text style={styles.recordText}>按住录音</Text>/;/g/;
              </TouchableOpacity>/;/g/;
            </View>/;/g/;
            <Text style={styles.instructionText}>;

            </Text>/;/g/;
            <Button;  />/;,/g/;
onPress={nextStep}
              style={styles.nextButton});
            />)/;/g/;
          </View>)/;/g/;
        );";"";
";,"";
case 'inquiry': ';,'';
return (<View style={styles.contentContainer}>;)            <Text style={styles.contentTitle}>症状问诊</Text>/;/g/;
            <View style={styles.questionContainer}>;
              <Text style={styles.questionText}>请选择您目前的症状：</Text>/;/g/;
              <View style={styles.symptomsGrid}>;

                    <TouchableOpacity;  />/;,/g/;
key={symptom}
                      style={styles.symptomButton}
                    >);
                      <Text style={styles.symptomText}>{symptom}</Text>)/;/g/;
                    </TouchableOpacity>)/;/g/;
                  );
                )}
              </View>/;/g/;
            </View>/;/g/;
            <Button;  />/;,/g/;
onPress={nextStep}
              style={styles.nextButton}
            />/;/g/;
          </View>/;/g/;
        );';'';
';,'';
case 'palpation': ';,'';
return (<View style={styles.contentContainer}>;)            <Text style={styles.contentTitle}>脉诊检测</Text>/;/g/;
            <View style={styles.pulseContainer}>;
              <Text style={styles.instructionText}>;

              </Text>'/;'/g'/;
              <View style={styles.pulseIndicator}>';'';
                <Icon name="heart-pulse" size={64} color={colors.info}  />"/;"/g"/;
                <Text style={styles.pulseText}>检测中...</Text>/;/g/;
              </View>/;/g/;
            </View>/;/g/;
            <Button;  />/;,/g/;
onPress={nextStep}
              style={styles.nextButton});
            />)/;/g/;
          </View>)/;/g/;
        );
default: ;
return null;
    }
  };

  // 渲染诊断结果/;,/g/;
const  renderDiagnosisResult = useCallback(() => {if (!diagnosisResult) return null;}}
}
    return (<View style={styles.resultContainer}>";)        <View style={styles.resultHeader}>";"";
          <Icon name="medical-bag" size={32} color={colors.primary}  />"/;"/g"/;
          <Text style={styles.resultTitle}>诊断结果</Text>/;/g/;
        </View>/;/g/;

        <View style={styles.syndromeCard}>;
          <Text style={styles.syndromeTitle}>证候诊断</Text>/;/g/;
          <Text style={styles.syndromeName}>{diagnosisResult.syndrome}</Text>/;/g/;
          <View style={styles.confidenceContainer}>;
            <Text style={styles.confidenceLabel}>可信度：</Text>/;/g/;
            <Text style={styles.confidenceValue}>;
              {diagnosisResult.confidence}%;
            </Text>/;/g/;
          </View>/;/g/;
        </View>/;/g/;
);
        <View style={styles.symptomsCard}>);
          <Text style={styles.cardTitle}>主要症状</Text>)"/;"/g"/;
          {diagnosisResult.symptoms.map(symptom, index) => (<View key={index} style={styles.symptomItem}>";)              <Icon name="circle-small" size={16} color={colors.primary}  />")""/;"/g"/;
              <Text style={styles.symptomItemText}>{symptom}</Text>)/;/g/;
            </View>)/;/g/;
          ))}
        </View>/;/g/;

        <View style={styles.recommendationsCard}>;
          <Text style={styles.cardTitle}>调理建议</Text>/;/g/;
          {diagnosisResult.recommendations.map(recommendation, index) => (<View key={index} style={styles.recommendationItem}>;)              <Text style={styles.recommendationNumber}>{index + 1}</Text>)/;/g/;
              <Text style={styles.recommendationText}>{recommendation}</Text>)/;/g/;
            </View>)/;/g/;
          ))}
        </View>/;/g/;

        {diagnosisResult.prescription && (<View style={styles.prescriptionCard}>;)            <Text style={styles.cardTitle}>推荐方剂</Text>/;/g/;
            <Text style={styles.prescriptionText}>;
              {diagnosisResult.prescription});
            </Text>)/;/g/;
          </View>)/;/g/;
        )}

        <View style={styles.actionButtons}>;
          <Button;  />/;,/g/;
style={styles.actionButton}
          />/;/g/;
          <Button;  />/;/g/;
";,"";
onPress={restart}";,"";
variant="outline";
style={styles.actionButton}
          />/;/g/;
        </View>/;/g/;
      </View>/;/g/;
    );
  };

  // 渲染处理中状态/;,/g/;
const  renderProcessing = () => (<View style={styles.processingContainer}>;)      <Animated.View;  />/;,/g/;
style={[;,]styles.processingIcon,;}          {const transform = [;]              {}                rotate: fadeAnim.interpolate({,)";}];,"";
inputRange: [0, 1],)";"";
}
                  outputRange: ['0deg', '360deg']')'}'';'';
                ;});
              }
            ];
          }
        ]}';'';
      >';'';
        <Icon name="brain" size={64} color={colors.primary}  />"/;"/g"/;
      </Animated.View>/;/g/;
      <Text style={styles.processingTitle}>AI 智能分析中</Text>/;/g/;
      <Text style={styles.processingText}>;

      </Text>/;/g/;
      <ProgressBar progress={progress} style={styles.processingProgress}  />/;/g/;
    </View>/;/g/;
  );
return (<SafeAreaView style={styles.container}>;)      {// 头部}/;/g/;
      <View style={styles.header}>);
        <TouchableOpacity;)  />/;,/g/;
style={styles.backButton});
onPress={() => navigation.goBack()}";"";
        >";"";
          <Icon name="arrow-left" size={24} color={colors.text}  />"/;"/g"/;
        </TouchableOpacity>/;/g/;
        <Text style={styles.headerTitle}>中医四诊</Text>"/;"/g"/;
        <TouchableOpacity style={styles.helpButton}>";"";
          <Icon name="help-circle-outline" size={24} color={colors.text}  />"/;"/g"/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;

      {// 进度条}/;/g/;
      <View style={styles.progressContainer}>;
        <ProgressBar progress={progress} style={styles.progressBar}  />/;/g/;
        <Text style={styles.progressText}>{Math.round(progress)}% 完成</Text>/;/g/;
      </View>/;/g/;

      {// 内容区域}/;/g/;
      <ScrollView;  />/;,/g/;
ref={scrollViewRef}
        style={styles.content}
        showsVerticalScrollIndicator={false}
      >;
        {isProcessing ? ();,}renderProcessing();
        ) : diagnosisResult ? ();
renderDiagnosisResult();
}
        ) : ()}
          <View style={styles.stepsContainer}>{steps.map(renderStepCard)}</View>/;/g/;
        )}
      </ScrollView>/;/g/;
    </SafeAreaView>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {flex: 1,;
}
    const backgroundColor = colors.background}
  ;},";,"";
header: {,";,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'space-between';','';
paddingHorizontal: spacing.lg,;
paddingVertical: spacing.md,;
backgroundColor: colors.surface,;
borderBottomWidth: 1,;
}
    const borderBottomColor = colors.border}
  ;}
backButton: {width: 40,;
height: 40,;
borderRadius: 20,';,'';
backgroundColor: colors.gray100,';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
headerTitle: {,';,}fontSize: typography.fontSize.lg,';,'';
fontWeight: '600' as const;','';'';
}
    const color = colors.text}
  ;}
helpButton: {width: 40,;
height: 40,;
borderRadius: 20,';,'';
backgroundColor: colors.gray100,';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
progressContainer: {paddingHorizontal: spacing.lg,;
paddingVertical: spacing.md,;
}
    const backgroundColor = colors.surface}
  ;}
progressBar: {,;}}
  const marginBottom = spacing.xs}
  ;}
progressText: {fontSize: typography.fontSize.sm,';,'';
color: colors.textSecondary,';'';
}
    const textAlign = 'center'}'';'';
  ;}
content: {,;}}
  const flex = 1}
  ;}
stepsContainer: {,;}}
  const padding = spacing.lg}
  ;}
stepCard: {backgroundColor: colors.surface,;
borderRadius: borderRadius.lg,;
padding: spacing.lg,;
marginBottom: spacing.lg,;
borderWidth: 1,;
const borderColor = colors.border;
}
    ...shadows.sm}
  }
activeStepCard: {const borderColor = colors.primary;
}
    ...shadows.md}
  },';,'';
completedStepCard: {,';,}backgroundColor: colors.success + '10';','';'';
}
    const borderColor = colors.success}
  ;},';,'';
stepHeader: {,';,}flexDirection: 'row';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
stepIcon: {width: 48,;
height: 48,';,'';
borderRadius: 24,';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
completedStepIcon: {,;}}
  const backgroundColor = colors.success}
  ;}
stepInfo: {flex: 1,;
}
    const marginLeft = spacing.md}
  ;}
stepTitle: {,';,}fontSize: typography.fontSize.lg,';,'';
fontWeight: '600' as const;','';'';
}
    const color = colors.text}
  ;}
activeStepTitle: {,;}}
  const color = colors.primary}
  ;}
stepDescription: {fontSize: typography.fontSize.sm,;
color: colors.textSecondary,;
}
    const marginTop = 2}
  ;}
stepStatus: {width: 24,';,'';
height: 24,';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
activeIndicator: {width: 12,;
height: 12,;
borderRadius: 6,;
}
    const backgroundColor = colors.primary}
  ;}
stepContent: {marginTop: spacing.lg,;
paddingTop: spacing.lg,;
borderTopWidth: 1,;
}
    const borderTopColor = colors.border}
  ;},';,'';
contentContainer: {,';}}'';
  const alignItems = 'center'}'';'';
  ;}
contentTitle: {,';,}fontSize: typography.fontSize.base,';,'';
fontWeight: '600' as const;','';
color: colors.text,';,'';
marginBottom: spacing.lg,';'';
}
    const textAlign = 'center'}'';'';
  ;},';,'';
uploadContainer: {,';,}flexDirection: 'row';','';
justifyContent: 'space-around';','';
width: '100%';','';'';
}
    const marginBottom = spacing.lg}
  ;},';,'';
uploadButton: {,';,}alignItems: 'center';','';
padding: spacing.lg,;
borderWidth: 2,';,'';
borderColor: colors.primary,';,'';
borderStyle: 'dashed';','';
borderRadius: borderRadius.md,';'';
}
    const width = '45%'}'';'';
  ;}
uploadText: {fontSize: typography.fontSize.sm,;
color: colors.primary,';,'';
marginTop: spacing.sm,';'';
}
    const textAlign = 'center'}'';'';
  ;},';,'';
recordContainer: {,';,}alignItems: 'center';','';'';
}
    const marginBottom = spacing.lg}
  ;}
recordButton: {width: 120,;
height: 120,';,'';
borderRadius: 60,';,'';
backgroundColor: colors.secondary + '20';','';
justifyContent: 'center';','';
alignItems: 'center';','';
borderWidth: 3,;
}
    const borderColor = colors.secondary}
  ;}
recordText: {fontSize: typography.fontSize.sm,;
color: colors.secondary,;
}
    const marginTop = spacing.sm}
  ;}
instructionText: {fontSize: typography.fontSize.sm,';,'';
color: colors.textSecondary,';,'';
textAlign: 'center';','';
marginBottom: spacing.lg,;
}
    const lineHeight = 20}
  ;},';,'';
questionContainer: {,';,}width: '100%';','';'';
}
    const marginBottom = spacing.lg}
  ;}
questionText: {fontSize: typography.fontSize.base,;
color: colors.text,;
}
    const marginBottom = spacing.md}
  ;},';,'';
symptomsGrid: {,';,}flexDirection: 'row';','';
flexWrap: 'wrap';','';'';
}
    const justifyContent = 'space-between'}'';'';
  ;},';,'';
symptomButton: {,';,}width: '48%';','';
padding: spacing.md,;
backgroundColor: colors.gray100,;
borderRadius: borderRadius.md,';,'';
marginBottom: spacing.sm,';'';
}
    const alignItems = 'center'}'';'';
  ;}
symptomText: {fontSize: typography.fontSize.sm,;
}
    const color = colors.text}
  ;},';,'';
pulseContainer: {,';,}alignItems: 'center';','';'';
}
    const marginBottom = spacing.lg}
  ;},';,'';
pulseIndicator: {,';,}alignItems: 'center';','';'';
}
    const marginTop = spacing.lg}
  ;}
pulseText: {fontSize: typography.fontSize.base,;
color: colors.info,;
}
    const marginTop = spacing.sm}
  ;},';,'';
nextButton: {,';}}'';
  const width = '100%'}'';'';
  ;}
processingContainer: {,';,}flex: 1,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const padding = spacing.xl}
  ;}
processingIcon: {,;}}
  const marginBottom = spacing.lg}
  ;}
processingTitle: {,';,}fontSize: typography.fontSize.xl,';,'';
fontWeight: '600' as const;','';
color: colors.text,;
}
    const marginBottom = spacing.sm}
  ;}
processingText: {fontSize: typography.fontSize.base,';,'';
color: colors.textSecondary,';,'';
textAlign: 'center';','';
marginBottom: spacing.xl,;
}
    const lineHeight = 22}
  ;},';,'';
processingProgress: {,';}}'';
  const width = '80%'}'';'';
  ;}
resultContainer: {,;}}
  const padding = spacing.lg}
  ;},';,'';
resultHeader: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'center';','';'';
}
    const marginBottom = spacing.xl}
  ;}
resultTitle: {,';,}fontSize: typography.fontSize.xl,';,'';
fontWeight: '600' as const;','';
color: colors.text,;
}
    const marginLeft = spacing.sm}
  ;},';,'';
syndromeCard: {,';,}backgroundColor: colors.primary + '10';','';
borderRadius: borderRadius.lg,;
padding: spacing.lg,;
marginBottom: spacing.lg,;
borderWidth: 1,;
}
    const borderColor = colors.primary}
  ;}
syndromeTitle: {fontSize: typography.fontSize.sm,;
color: colors.primary,;
}
    const marginBottom = spacing.xs}
  ;}
syndromeName: {,';,}fontSize: typography.fontSize.xl,';,'';
fontWeight: '700' as const;','';
color: colors.primary,;
}
    const marginBottom = spacing.sm}
  ;},';,'';
confidenceContainer: {,';,}flexDirection: 'row';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
confidenceLabel: {fontSize: typography.fontSize.sm,;
}
    const color = colors.textSecondary}
  ;}
confidenceValue: {,';,}fontSize: typography.fontSize.sm,';,'';
fontWeight: '600' as const;','';'';
}
    const color = colors.primary}
  ;}
symptomsCard: {backgroundColor: colors.surface,;
borderRadius: borderRadius.lg,;
padding: spacing.lg,;
const marginBottom = spacing.lg;
}
    ...shadows.sm}
  }
cardTitle: {,';,}fontSize: typography.fontSize.base,';,'';
fontWeight: '600' as const;','';
color: colors.text,;
}
    const marginBottom = spacing.md}
  ;},';,'';
symptomItem: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = spacing.xs}
  ;}
symptomItemText: {fontSize: typography.fontSize.sm,;
color: colors.text,;
}
    const marginLeft = spacing.xs}
  ;}
recommendationsCard: {backgroundColor: colors.surface,;
borderRadius: borderRadius.lg,;
padding: spacing.lg,;
const marginBottom = spacing.lg;
}
    ...shadows.sm}
  },';,'';
recommendationItem: {,';,}flexDirection: 'row';','';'';
}
    const marginBottom = spacing.sm}
  ;}
recommendationNumber: {width: 20,;
height: 20,;
borderRadius: 10,;
backgroundColor: colors.primary,;
color: colors.white,';,'';
fontSize: typography.fontSize.xs,';,'';
textAlign: 'center';','';
lineHeight: 20,;
}
    const marginRight = spacing.sm}
  ;}
recommendationText: {flex: 1,;
fontSize: typography.fontSize.sm,;
color: colors.text,;
}
    const lineHeight = 20}
  ;},';,'';
prescriptionCard: {,';,}backgroundColor: colors.warning + '10';','';
borderRadius: borderRadius.lg,;
padding: spacing.lg,;
marginBottom: spacing.lg,;
borderWidth: 1,;
}
    const borderColor = colors.warning}
  ;}
prescriptionText: {,';,}fontSize: typography.fontSize.base,';,'';
fontWeight: '600' as const;','';'';
}
    const color = colors.warning}
  ;},';,'';
actionButtons: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';'';
}
    const marginTop = spacing.lg}
  ;},';,'';
actionButton: {,')'';}}'';
  const width = '48%')}'';'';
  ;});
});
export default EnhancedDiagnosisScreen;';'';
''';