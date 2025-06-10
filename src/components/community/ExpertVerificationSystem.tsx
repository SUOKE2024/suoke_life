import React, { useCallback, useEffect, useState } from "react";";
import {ActivityIndicator}Alert,;
Dimensions,;
Image,;
Modal,;
ScrollView,;
StyleSheet,;
Text,;
TextInput,;
TouchableOpacity,";"";
}
    View'}'';'';
} from "react-native";";
import { SafeAreaView } from "react-native-safe-area-context";";
import Icon from "react-native-vector-icons/MaterialCommunityIcons";""/;,"/g"/;
import { borderRadius, colors, spacing, typography } from "../../constants/theme";""/;"/g"/;
';,'';
const { width } = Dimensions.get('window');';,'';
interface ExpertProfile {id: string}userId: string,;
const name = string;
avatar?: string;
title: string,;
institution: string,;
specialties: string[],';,'';
credentials: ExpertCredential[],';,'';
verificationStatus: 'pending' | 'verified' | 'rejected' | 'suspended';','';
verificationLevel: 'junior' | 'senior' | 'authority';','';
credibilityScore: number,;
metrics: ExpertMetrics,;
bio: string,;
contactInfo: ContactInfo,;
const createdAt = string;
}
}
  verifiedAt?: string;}
}

interface ExpertCredential {';,}id: string,';,'';
type: 'education' | 'certification' | 'license' | 'publication' | 'award';','';
title: string,;
institution: string,;
const year = number;';,'';
documentUrl?: string;';'';
}
}
  const verificationStatus = 'pending' | 'verified' | 'rejected';'}'';'';
}

interface ExpertMetrics {answersCount: number}helpfulAnswers: number,;
answerAcceptanceRate: number,;
averageRating: number,;
knowledgeContributions: number,;
peerEndorsements: number,;
consultationHours: number,;
}
}
  const patientSatisfaction = number;}
}

interface ContactInfo {const email = string;,}phone?: string;
website?: string;
}
}
  socialMedia?: Record<string; string>;}
}

interface ExpertVerificationSystemProps {currentUser?: any;,}onExpertVerified?: (expert: ExpertProfile) => void;
}
}
  onApplicationSubmitted?: (application: any) => void;}
}

const  ExpertVerificationSystem: React.FC<ExpertVerificationSystemProps> = ({)currentUser,);,}onExpertVerified,);
}
  onApplicationSubmitted)}';'';
;}) => {';,}const [activeTab, setActiveTab] = useState<'apply' | 'experts' | 'manage'>('experts');';,'';
const [experts, setExperts] = useState<ExpertProfile[]>([]);
const [loading, setLoading] = useState(false);
const [selectedExpert, setSelectedExpert] = useState<ExpertProfile | null>(null);
const [showExpertDetail, setShowExpertDetail] = useState(false);
const [showApplicationForm, setShowApplicationForm] = useState(false);

  // 专家申请表单状态'/;,'/g'/;
const [applicationForm, setApplicationForm] = useState({';,)name: ';',';,}title: ';',';,'';
institution: ';',';,'';
specialties: [] as string[],';,'';
bio: ';',';,'';
email: ';',')'';
phone: ';',')'';'';
}
    const credentials = [] as Partial<ExpertCredential>[])}
  ;});

  // 专业领域配置/;,/g/;
const  specialtyOptions = [;]];
  ];

  // 认证等级配置/;,/g/;
const  verificationLevels = {junior: {,;}';,'';
color: colors.info,';,'';
const icon = 'star-outline';';'';
}
}
    }
senior: {,;}';,'';
color: colors.warning,';,'';
const icon = 'star-half-full';';'';
}
}
    }
authority: {,;}';,'';
color: colors.success,';,'';
const icon = 'star';';'';
}
}
    }
  };
useEffect(() => {loadExperts();,}return () => {}}
        // 清理函数}/;/g/;
      };
    }, []);
const  loadExperts = useCallback(async () => {setLoading(true);,}try {// 模拟API调用/;,}const  mockExperts: ExpertProfile[] = [;]';'/g'/;
        {';,}id: '1';','';
userId: 'user_1';','';'';
';,'';
avatar: 'https://example.com/avatar1.jpg';',''/;'/g'/;
';'';
';'';
];
specialties: ['tcm_internal', 'herbal_medicine'],';,'';
const credentials = [;]';'';
            {';,}id: '1';','';
type: 'education';','';'';
';,'';
year: 2005,';'';
}
              const verificationStatus = 'verified'}'';'';
            ;}';'';
];
          ],';,'';
verificationStatus: 'verified';','';
verificationLevel: 'authority';','';
credibilityScore: 0.95,;
metrics: {answersCount: 156,;
helpfulAnswers: 142,;
answerAcceptanceRate: 0.91,;
averageRating: 4.8,;
knowledgeContributions: 23,;
peerEndorsements: 45,;
consultationHours: 320,;
}
            const patientSatisfaction = 0.94}
          ;}
';,'';
contactInfo: {,';,}email: 'wang.prof@example.com';','';'';
}
            const website = 'https://wang-tcm.com'}'/;'/g'/;
          ;},';,'';
createdAt: '2023-01-15';','';
const verifiedAt = '2023-02-01'';'';
        ;},';'';
        {';,}id: '2';','';
userId: 'user_2';','';'';
';'';
';,'';
specialties: ['acupuncture', 'rehabilitation'],';,'';
credentials: [],';,'';
verificationStatus: 'verified';','';
verificationLevel: 'senior';','';
credibilityScore: 0.88,;
metrics: {answersCount: 89,;
helpfulAnswers: 76,;
answerAcceptanceRate: 0.85,;
averageRating: 4.6,;
knowledgeContributions: 15,;
peerEndorsements: 28,;
consultationHours: 180,;
}
            const patientSatisfaction = 0.89}
          ;}
';,'';
contactInfo: {,';}}'';
            const email = 'li.doctor@example.com'}';'';
          ;},';,'';
createdAt: '2023-03-10';','';
const verifiedAt = '2023-03-25'';'';
        ;}
      ];
setExperts(mockExperts);
    } catch (error) {}}
}
    } finally {}}
      setLoading(false);}
    }
  }, []);
const  handleSubmitApplication = useCallback(async () => {if (!applicationForm.name || !applicationForm.title || !applicationForm.institution) {}}
      return;}
    }

    if (applicationForm.specialties.length === 0) {}}
      return;}
    }

    if (applicationForm.credentials.length === 0) {}}
      return;}
    }

    try {setLoading(true);}      // 模拟提交申请/;,/g,/;
  await: new Promise(resolve => setTimeout(resolve, 2000));
setShowApplicationForm(false);';,'';
setApplicationForm({';,)name: ';',';,}title: ';',';,'';
institution: ';',';,'';
specialties: [],';,'';
bio: ';',';,'';
email: ';',')'';
phone: ';',')'';'';
}
        const credentials = [])}
      ;});
onApplicationSubmitted?.(applicationForm);
    } catch (error) {}}
}
    } finally {}}
      setLoading(false);}
    }
  }, [applicationForm, onApplicationSubmitted]);
const  renderExpertCard = (expert: ExpertProfile) => {const levelConfig = verificationLevels[expert.verificationLevel];}}
    return (<TouchableOpacity,)}  />/;,/g/;
key={expert.id});
style={styles.expertCard});
onPress={() => {}          setSelectedExpert(expert);
}
          setShowExpertDetail(true);}
        }}
      >;
        <View style={styles.expertHeader}>;
          <View style={styles.expertAvatar}>';'';
            {expert.avatar ? (<Image source={{ uri: expert.avatar ;}} style={styles.avatarImage}  />)'/;'/g'/;
            ) : (<Icon name="account" size={32} color={colors.textSecondary}  />")""/;"/g"/;
            )}
          </View>/;/g/;

          <View style={styles.expertInfo}>;
            <View style={styles.expertNameRow}>;
              <Text style={styles.expertName}>{expert.name}</Text>"/;"/g"/;
              <View style={[styles.verificationBadge, { backgroundColor: levelConfig.color ;}]}>";"";
                <Icon name={levelConfig.icon} size={12} color="white"  />"/;"/g"/;
                <Text style={styles.verificationText}>{levelConfig.name}</Text>/;/g/;
              </View>/;/g/;
            </View>/;/g/;

            <Text style={styles.expertTitle}>{expert.title}</Text>/;/g/;
            <Text style={styles.expertInstitution}>{expert.institution}</Text>/;/g/;

            <View style={styles.specialtyTags}>;
              {expert.specialties.slice(0, 2).map(specialtyId => {);}}
                const specialty = specialtyOptions.find(s => s.id === specialtyId);}
                const return = specialty ? (<View key={specialtyId} style={styles.specialtyTag}>);
                    <Text style={styles.specialtyTagText}>{specialty.name}</Text>)/;/g/;
                  </View>)/;/g/;
                ) : null;
              })}
              {expert.specialties.length > 2 && (<Text style={styles.moreSpecialties}>+{expert.specialties.length - 2}</Text>)/;/g/;
              )}
            </View>/;/g/;
          </View>/;/g/;
        </View>/;/g/;

        <View style={styles.expertMetrics}>;
          <View style={styles.metricItem}>;
            <Text style={styles.metricValue}>{expert.metrics.answersCount}</Text>/;/g/;
            <Text style={styles.metricLabel}>回答</Text>/;/g/;
          </View>/;/g/;
          <View style={styles.metricItem}>;
            <Text style={styles.metricValue}>{expert.metrics.averageRating.toFixed(1)}</Text>/;/g/;
            <Text style={styles.metricLabel}>评分</Text>/;/g/;
          </View>/;/g/;
          <View style={styles.metricItem}>;
            <Text style={styles.metricValue}>{(expert.credibilityScore * 100).toFixed(0)}%</Text>/;/g/;
            <Text style={styles.metricLabel}>可信度</Text>/;/g/;
          </View>/;/g/;
        </View>/;/g/;
      </TouchableOpacity>/;/g/;
    );
  };
const: renderApplicationForm = () => (<Modal,"  />/;,)visible={showApplicationForm}")"";,"/g"/;
animationType="slide")";,"";
presentationStyle="pageSheet")";,"";
onRequestClose={() => setShowApplicationForm(false)}
    >;
      <SafeAreaView style={styles.modalContainer}>;
        <View style={styles.modalHeader}>";"";
          <TouchableOpacity onPress={() => setShowApplicationForm(false)}>";"";
            <Icon name="close" size={24} color={colors.text}  />"/;"/g"/;
          </TouchableOpacity>/;/g/;
          <Text style={styles.modalTitle}>专家认证申请</Text>/;/g/;
          <TouchableOpacity onPress={handleSubmitApplication} disabled={loading}>;
            <Text style={[styles.submitButton, loading && styles.disabledButton]}>;

            </Text>/;/g/;
          </TouchableOpacity>/;/g/;
        </View>/;/g/;

        <ScrollView style={styles.formContainer}>;
          {/* 基本信息 */}/;/g/;
          <View style={styles.formSection}>;
            <Text style={styles.sectionTitle}>基本信息</Text>/;/g/;

            <View style={styles.inputGroup}>;
              <Text style={styles.inputLabel}>姓名 *</Text>/;/g/;
              <TextInput,  />/;,/g/;
style={styles.textInput}

                value={applicationForm.name}
                onChangeText={(text) => setApplicationForm(prev => ({ ...prev, name: text ;}))}
              />/;/g/;
            </View>/;/g/;

            <View style={styles.inputGroup}>;
              <Text style={styles.inputLabel}>职称 *</Text>/;/g/;
              <TextInput,  />/;,/g/;
style={styles.textInput}

                value={applicationForm.title}
                onChangeText={(text) => setApplicationForm(prev => ({ ...prev, title: text ;}))}
              />/;/g/;
            </View>/;/g/;

            <View style={styles.inputGroup}>;
              <Text style={styles.inputLabel}>所属机构 *</Text>/;/g/;
              <TextInput,  />/;,/g/;
style={styles.textInput}

                value={applicationForm.institution}
                onChangeText={(text) => setApplicationForm(prev => ({ ...prev, institution: text ;}))}
              />/;/g/;
            </View>/;/g/;

            <View style={styles.inputGroup}>;
              <Text style={styles.inputLabel}>个人简介</Text>/;/g/;
              <TextInput,  />/;,/g/;
style={[styles.textInput, styles.textArea]}

                value={applicationForm.bio}
                onChangeText={(text) => setApplicationForm(prev => ({ ...prev, bio: text ;}))}";,"";
multiline,";,"";
textAlignVertical="top"";"";
              />/;/g/;
            </View>/;/g/;
          </View>/;/g/;

          {/* 专业领域 */}/;/g/;
          <View style={styles.formSection}>;
            <Text style={styles.sectionTitle}>专业领域 *</Text>/;/g/;
            <View style={styles.specialtyGrid}>;
              {}specialtyOptions.map(specialty => (;)}
                <TouchableOpacity,}  />/;,/g/;
key={specialty.id});
style={[;]);,}styles.specialtyOption,);
}
                    applicationForm.specialties.includes(specialty.id) && styles.selectedSpecialty}
];
                  ]}
                  onPress={() => {}                    setApplicationForm(prev => ({);}                      ...prev,);
const specialties = prev.specialties.includes(specialty.id);
                        ? prev.specialties.filter(s => s !== specialty.id);
}
                        : [...prev.specialties, specialty.id]}
                    ;}));
                  }}
                >;
                  <Icon  />/;,/g/;
name={specialty.icon}
                    size={20}
                    color={applicationForm.specialties.includes(specialty.id) ? colors.primary : colors.textSecondary}
                  />/;/g/;
                  <Text style={ />/;}[;,]styles.specialtyOptionText,;/g/;
}
                    applicationForm.specialties.includes(specialty.id) && styles.selectedSpecialtyText}
];
                  ]}>;
                    {specialty.name}
                  </Text>/;/g/;
                </TouchableOpacity>/;/g/;
              ))}
            </View>/;/g/;
          </View>/;/g/;

          {/* 联系方式 */}/;/g/;
          <View style={styles.formSection}>;
            <Text style={styles.sectionTitle}>联系方式</Text>/;/g/;

            <View style={styles.inputGroup}>;
              <Text style={styles.inputLabel}>邮箱 *</Text>/;/g/;
              <TextInput,  />/;,/g/;
style={styles.textInput}

                value={applicationForm.email}";,"";
onChangeText={(text) => setApplicationForm(prev => ({ ...prev, email: text ;}))}";,"";
keyboardType="email-address"";"";
              />/;/g/;
            </View>/;/g/;

            <View style={styles.inputGroup}>;
              <Text style={styles.inputLabel}>电话</Text>/;/g/;
              <TextInput,  />/;,/g/;
style={styles.textInput}

                value={applicationForm.phone}";,"";
onChangeText={(text) => setApplicationForm(prev => ({ ...prev, phone: text ;}))}";,"";
keyboardType="phone-pad"";"";
              />/;/g/;
            </View>/;/g/;
          </View>/;/g/;

          {/* 资质证明 */}/;/g/;
          <View style={styles.formSection}>;
            <Text style={styles.sectionTitle}>资质证明 *</Text>/;/g/;
            <Text style={styles.sectionDescription}>;

            </Text>/;/g/;

            <TouchableOpacity,  />/;,/g/;
style={styles.addCredentialButton}
              onPress={() => {}                setApplicationForm(prev => ({)                  ...prev,";,}credentials: [;]...prev.credentials, {";,}type: 'education';',')';,'';
title: ';',)';,'';
institution: ';',)';'';
}
                    const year = new Date().getFullYear()}
];
                  ;}];
                }));
              }}';'';
            >';'';
              <Icon name="plus" size={20} color={colors.primary}  />"/;"/g"/;
              <Text style={styles.addCredentialText}>添加资质证明</Text>/;/g/;
            </TouchableOpacity>/;/g/;

            {applicationForm.credentials.map((credential, index) => (<View key={index} style={styles.credentialItem}>;)                <View style={styles.credentialHeader}>);
                  <Text style={styles.credentialTitle}>证明 {index + 1}</Text>)/;/g/;
                  <TouchableOpacity,)  />/;,/g/;
onPress={() => {}                      setApplicationForm(prev => ({);}                        ...prev,);
}
                        credentials: prev.credentials.filter((_, i) => i !== index)}
                      ;}));
                    }}";"";
                  >";"";
                    <Icon name="delete" size={20} color={colors.error}  />"/;"/g"/;
                  </TouchableOpacity>/;/g/;
                </View>/;/g/;

                <TextInput,  />/;,/g/;
style={styles.textInput}

                  value={credential.title}
                  onChangeText={(text) => {}                    setApplicationForm(prev => ({);}                      ...prev,);
}
                      credentials: prev.credentials.map((c, i) => }
                        i === index ? { ...c, title: text ;} : c;
                      );
                    }));
                  }}
                />/;/g/;

                <TextInput,  />/;,/g/;
style={styles.textInput}

                  value={credential.institution}
                  onChangeText={(text) => {}                    setApplicationForm(prev => ({);}                      ...prev,);
}
                      credentials: prev.credentials.map((c, i) => }
                        i === index ? { ...c, institution: text ;} : c;
                      );
                    }));
                  }}
                />/;/g/;
              </View>/;/g/;
            ))}
          </View>/;/g/;
        </ScrollView>/;/g/;
      </SafeAreaView>/;/g/;
    </Modal>/;/g/;
  );
const: renderExpertDetail = () => (<Modal,"  />/;,)visible={showExpertDetail}")"";,"/g"/;
animationType="slide")";,"";
presentationStyle="pageSheet")";,"";
onRequestClose={() => setShowExpertDetail(false)}
    >;
      <SafeAreaView style={styles.modalContainer}>;
        <View style={styles.modalHeader}>";"";
          <TouchableOpacity onPress={() => setShowExpertDetail(false)}>";"";
            <Icon name="arrow-left" size={24} color={colors.text}  />"/;"/g"/;
          </TouchableOpacity>/;/g/;
          <Text style={styles.modalTitle}>专家详情</Text>/;/g/;
          <View style={{ width: 24 ;}}  />/;/g/;
        </View>/;/g/;

        {selectedExpert && (<ScrollView style={styles.expertDetailContainer}>;)            {/* 专家基本信息 */}/;/g/;
            <View style={styles.expertDetailHeader}>;
              <View style={styles.expertDetailAvatar}>);
                {selectedExpert.avatar ? ()}";"";
                  <Image source={{ uri: selectedExpert.avatar ;}} style={styles.detailAvatarImage}  />)"/;"/g"/;
                ) : (<Icon name="account" size={48} color={colors.textSecondary}  />")""/;"/g"/;
                )}
              </View>/;/g/;

              <View style={styles.expertDetailInfo}>;
                <Text style={styles.expertDetailName}>{selectedExpert.name}</Text>/;/g/;
                <Text style={styles.expertDetailTitle}>{selectedExpert.title}</Text>/;/g/;
                <Text style={styles.expertDetailInstitution}>{selectedExpert.institution}</Text>/;/g/;

                <View style={styles.verificationInfo}>;
                  <View style={ />/;}[;]}/g/;
                    styles.verificationBadge, }
];
                    { backgroundColor: verificationLevels[selectedExpert.verificationLevel].color ;}
                  ]}>;
                    <Icon  />/;,/g/;
name={verificationLevels[selectedExpert.verificationLevel].icon} ";,"";
size={12} ";,"";
color="white" ";"";
                    />/;/g/;
                    <Text style={styles.verificationText}>;
                      {verificationLevels[selectedExpert.verificationLevel].name}
                    </Text>/;/g/;
                  </View>/;/g/;
                  <Text style={styles.credibilityScore}>;
                    可信度: {(selectedExpert.credibilityScore * 100).toFixed(0)}%;
                  </Text>/;/g/;
                </View>/;/g/;
              </View>/;/g/;
            </View>/;/g/;

            {/* 专业领域 */}/;/g/;
            <View style={styles.detailSection}>;
              <Text style={styles.detailSectionTitle}>专业领域</Text>/;/g/;
              <View style={styles.specialtyTags}>;
                {selectedExpert.specialties.map(specialtyId => {);}}
                  const specialty = specialtyOptions.find(s => s.id === specialtyId);}
                  const return = specialty ? (<View key={specialtyId} style={styles.specialtyTag}>;)                      <Icon name={specialty.icon} size={14} color={colors.primary}  />)/;/g/;
                      <Text style={styles.specialtyTagText}>{specialty.name}</Text>)/;/g/;
                    </View>)/;/g/;
                  ) : null;
                })}
              </View>/;/g/;
            </View>/;/g/;

            {/* 个人简介 */}/;/g/;
            <View style={styles.detailSection}>;
              <Text style={styles.detailSectionTitle}>个人简介</Text>/;/g/;
              <Text style={styles.bioText}>{selectedExpert.bio}</Text>/;/g/;
            </View>/;/g/;

            {/* 专业数据 */}/;/g/;
            <View style={styles.detailSection}>;
              <Text style={styles.detailSectionTitle}>专业数据</Text>/;/g/;
              <View style={styles.metricsGrid}>;
                <View style={styles.metricCard}>;
                  <Text style={styles.metricCardValue}>{selectedExpert.metrics.answersCount}</Text>/;/g/;
                  <Text style={styles.metricCardLabel}>回答数量</Text>/;/g/;
                </View>/;/g/;
                <View style={styles.metricCard}>;
                  <Text style={styles.metricCardValue}>{selectedExpert.metrics.averageRating.toFixed(1)}</Text>/;/g/;
                  <Text style={styles.metricCardLabel}>平均评分</Text>/;/g/;
                </View>/;/g/;
                <View style={styles.metricCard}>;
                  <Text style={styles.metricCardValue}>{(selectedExpert.metrics.answerAcceptanceRate * 100).toFixed(0)}%</Text>/;/g/;
                  <Text style={styles.metricCardLabel}>采纳率</Text>/;/g/;
                </View>/;/g/;
                <View style={styles.metricCard}>;
                  <Text style={styles.metricCardValue}>{selectedExpert.metrics.consultationHours}</Text>/;/g/;
                  <Text style={styles.metricCardLabel}>咨询时长</Text>/;/g/;
                </View>/;/g/;
              </View>/;/g/;
            </View>/;/g/;

            {/* 资质证明 */}/;/g/;
            {selectedExpert.credentials.length > 0 && (<View style={styles.detailSection}>;)                <Text style={styles.detailSectionTitle}>资质证明</Text>/;/g/;
                {selectedExpert.credentials.map(credential => (})                  <View key={credential.id} style={styles.credentialCard}>;
                    <View style={styles.credentialInfo}>;
                      <Text style={styles.credentialCardTitle}>{credential.title}</Text>/;/g/;
                      <Text style={styles.credentialInstitution}>{credential.institution}</Text>/;/g/;
                      <Text style={styles.credentialYear}>{credential.year}年</Text>/;/g/;
                    </View>/;/g/;
                    <View style={ />/;}[;]";"/g"/;
}
                      styles.credentialStatus,"}"";"";
                      { backgroundColor: credential.verificationStatus === 'verified' ? colors.success : colors.warning ;}';'';
];
                    ]}>';'';
                      <Icon '  />/;,'/g'/;
name={credential.verificationStatus === 'verified' ? 'check' : 'clock'} ';,'';
size={12} ';,'';
color="white" ";"";
                      />)/;/g/;
                    </View>)/;/g/;
                  </View>)/;/g/;
                ))}
              </View>/;/g/;
            )}
          </ScrollView>/;/g/;
        )}
      </SafeAreaView>/;/g/;
    </Modal>/;/g/;
  );
return (<SafeAreaView style={styles.container}>;)      {/* 标签页导航 */}/;/g/;
      <View style={styles.tabContainer}>)";"";
        <TouchableOpacity,)"  />/;,"/g"/;
style={[styles.tab, activeTab === 'experts' && styles.activeTab]}')'';
onPress={() => setActiveTab('experts')}';'';
        >';'';
          <Icon '  />/;,'/g'/;
name="account-group" ";,"";
size={20} ";,"";
color={activeTab === 'experts' ? colors.primary : colors.textSecondary} ';'';
          />'/;'/g'/;
          <Text style={[styles.tabText, activeTab === 'experts' && styles.activeTabText]}>';'';

          </Text>/;/g/;
        </TouchableOpacity>/;/g/;
        ';'';
        <TouchableOpacity,'  />/;,'/g'/;
style={[styles.tab, activeTab === 'apply' && styles.activeTab]}';,'';
onPress={() => setActiveTab('apply')}';'';
        >';'';
          <Icon '  />/;,'/g'/;
name="account-plus" ";,"";
size={20} ";,"";
color={activeTab === 'apply' ? colors.primary : colors.textSecondary} ';'';
          />'/;'/g'/;
          <Text style={[styles.tabText, activeTab === 'apply' && styles.activeTabText]}>';'';

          </Text>/;/g/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;
      ';'';
      {/* 内容区域 */}'/;'/g'/;
      {activeTab === 'experts' && ('}'';)        <View style={styles.content}>;'';
          <View style={styles.contentHeader}>;
            <Text style={styles.contentTitle}>认证专家</Text>/;/g/;
            <Text style={styles.contentSubtitle}>;

            </Text>/;/g/;
          </View>/;/g/;

          {loading ? (}';)            <View style={styles.loadingContainer}>')'';'';
              <ActivityIndicator size="large" color={colors.primary}  />")""/;"/g"/;
            </View>)/;/g/;
          ) : (<ScrollView style={styles.expertsList}>);
              {experts.map(renderExpertCard)}
            </ScrollView>/;/g/;
          )}
        </View>/;/g/;
      )}";"";
      ";"";
      {activeTab === 'apply' && ('}'';)        <View style={styles.content}>;'';
          <View style={styles.contentHeader}>;
            <Text style={styles.contentTitle}>专家认证申请</Text>/;/g/;
            <Text style={styles.contentSubtitle}>;

            </Text>/;/g/;
          </View>/;/g/;

          <ScrollView style={styles.applyContent}>;
            {/* 认证等级说明 */})/;/g/;
            <View style={styles.levelSection}>);
              <Text style={styles.levelSectionTitle}>认证等级</Text>)/;/g/;
              {Object.entries(verificationLevels).map(([level, config]) => (<View key={level} style={styles.levelCard}>;)                  <View style={styles.levelHeader}>';'';
                    <View style={[styles.levelIcon, { backgroundColor: config.color ;}]}>';'';
                      <Icon name={config.icon} size={20} color="white"  />"/;"/g"/;
                    </View>/;/g/;
                    <Text style={styles.levelName}>{config.name}</Text>)/;/g/;
                  </View>)/;/g/;
                  <View style={styles.levelRequirements}>);
                    {config.requirements.map((requirement, index) => (<Text key={index} style={styles.requirementText}>);
                        • {requirement});
                      </Text>)/;/g/;
                    ))}
                  </View>/;/g/;
                </View>/;/g/;
              ))}
            </View>/;/g/;

            {/* 申请按钮 */}/;/g/;
            <TouchableOpacity,  />/;,/g/;
style={styles.applyButton}
              onPress={() => setShowApplicationForm(true)}";"";
            >";"";
              <Icon name="account-plus" size={20} color="white"  />"/;"/g"/;
              <Text style={styles.applyButtonText}>开始申请认证</Text>/;/g/;
            </TouchableOpacity>/;/g/;
          </ScrollView>/;/g/;
        </View>/;/g/;
      )}

      {renderApplicationForm()}
      {renderExpertDetail()}
    </SafeAreaView>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {flex: 1,;
}
    const backgroundColor = colors.background;}
  },";,"";
tabContainer: {,";,}flexDirection: 'row';','';
backgroundColor: colors.surface,;
borderBottomWidth: 1,;
}
    const borderBottomColor = colors.border;}
  }
tab: {,';,}flex: 1,';,'';
flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'center';','';
paddingVertical: spacing.md,;
}
    const paddingHorizontal = spacing.sm;}
  }
activeTab: {borderBottomWidth: 2,;
}
    const borderBottomColor = colors.primary;}
  }
tabText: {marginLeft: spacing.xs,;
fontSize: typography.sizes.sm,;
}
    const color = colors.textSecondary;}
  }
activeTabText: {color: colors.primary,;
}
    const fontWeight = typography.weights.medium;}
  }
content: {,;}}
    const flex = 1;}
  }
contentHeader: {padding: spacing.md,;
}
    const backgroundColor = colors.surface;}
  }
contentTitle: {fontSize: typography.sizes.xl,;
fontWeight: typography.weights.bold,;
color: colors.text,;
}
    const marginBottom = spacing.xs;}
  }
contentSubtitle: {fontSize: typography.sizes.sm,;
color: colors.textSecondary,;
}
    const lineHeight = 20;}
  }
loadingContainer: {,';,}flex: 1,';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center';'}'';'';
  }
expertsList: {flex: 1,;
}
    const padding = spacing.md;}
  }
expertCard: {backgroundColor: colors.surface,;
borderRadius: borderRadius.lg,;
padding: spacing.md,;
marginBottom: spacing.md,;
borderWidth: 1,;
}
    const borderColor = colors.border;}
  },';,'';
expertHeader: {,';,}flexDirection: 'row';','';'';
}
    const marginBottom = spacing.md;}
  }
expertAvatar: {width: 60,;
height: 60,;
borderRadius: 30,';,'';
backgroundColor: colors.background,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const marginRight = spacing.md;}
  }
avatarImage: {width: 60,;
height: 60,;
}
    const borderRadius = 30;}
  }
expertInfo: {,;}}
    const flex = 1;}
  },';,'';
expertNameRow: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = spacing.xs;}
  }
expertName: {fontSize: typography.sizes.lg,;
fontWeight: typography.weights.semibold,;
color: colors.text,;
}
    const marginRight = spacing.sm;}
  },';,'';
verificationBadge: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
paddingHorizontal: spacing.xs,;
paddingVertical: 2,;
}
    const borderRadius = borderRadius.sm;}
  }
verificationText: {,';,}fontSize: typography.sizes.xs,';,'';
color: 'white';','';'';
}
    const marginLeft = 2;}
  }
expertTitle: {fontSize: typography.sizes.md,;
color: colors.text,;
}
    const marginBottom = spacing.xs;}
  }
expertInstitution: {fontSize: typography.sizes.sm,;
color: colors.textSecondary,;
}
    const marginBottom = spacing.sm;}
  },';,'';
specialtyTags: {,';,}flexDirection: 'row';','';
flexWrap: 'wrap';','';'';
}
    const alignItems = 'center';'}'';'';
  },';,'';
specialtyTag: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
backgroundColor: colors.primary + '20';','';
paddingHorizontal: spacing.xs,;
paddingVertical: 2,;
borderRadius: borderRadius.sm,;
marginRight: spacing.xs,;
}
    const marginBottom = spacing.xs;}
  }
specialtyTagText: {fontSize: typography.sizes.xs,;
color: colors.primary,;
}
    const marginLeft = 2;}
  }
moreSpecialties: {fontSize: typography.sizes.xs,;
}
    const color = colors.textSecondary;}
  },';,'';
expertMetrics: {,';,}flexDirection: 'row';','';
justifyContent: 'space-around';','';
paddingTop: spacing.md,;
borderTopWidth: 1,;
}
    const borderTopColor = colors.border;}
  },';,'';
metricItem: {,';}}'';
    const alignItems = 'center';'}'';'';
  }
metricValue: {fontSize: typography.sizes.lg,;
fontWeight: typography.weights.semibold,;
}
    const color = colors.primary;}
  }
metricLabel: {fontSize: typography.sizes.xs,;
color: colors.textSecondary,;
}
    const marginTop = spacing.xs;}
  }
modalContainer: {flex: 1,;
}
    const backgroundColor = colors.background;}
  },';,'';
modalHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';
paddingHorizontal: spacing.md,;
paddingVertical: spacing.md,;
borderBottomWidth: 1,;
}
    const borderBottomColor = colors.border;}
  }
modalTitle: {fontSize: typography.sizes.lg,;
fontWeight: typography.weights.semibold,;
}
    const color = colors.text;}
  }
submitButton: {color: colors.primary,;
fontSize: typography.sizes.sm,;
}
    const fontWeight = typography.weights.medium;}
  }
disabledButton: {,;}}
    const color = colors.textSecondary;}
  }
formContainer: {flex: 1,;
}
    const padding = spacing.md;}
  }
formSection: {,;}}
    const marginBottom = spacing.xl;}
  }
sectionTitle: {fontSize: typography.sizes.lg,;
fontWeight: typography.weights.semibold,;
color: colors.text,;
}
    const marginBottom = spacing.md;}
  }
sectionDescription: {fontSize: typography.sizes.sm,;
color: colors.textSecondary,;
marginBottom: spacing.md,;
}
    const lineHeight = 20;}
  }
inputGroup: {,;}}
    const marginBottom = spacing.md;}
  }
inputLabel: {fontSize: typography.sizes.md,;
fontWeight: typography.weights.medium,;
color: colors.text,;
}
    const marginBottom = spacing.sm;}
  }
textInput: {borderWidth: 1,;
borderColor: colors.border,;
borderRadius: borderRadius.md,;
paddingHorizontal: spacing.md,;
paddingVertical: spacing.sm,;
fontSize: typography.sizes.md,;
color: colors.text,;
}
    const backgroundColor = colors.surface;}
  }
textArea: {,';,}minHeight: 100,';'';
}
    const textAlignVertical = 'top';'}'';'';
  },';,'';
specialtyGrid: {,';,}flexDirection: 'row';','';'';
}
    const flexWrap = 'wrap';'}'';'';
  },';,'';
specialtyOption: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
paddingHorizontal: spacing.md,;
paddingVertical: spacing.sm,;
borderWidth: 1,;
borderColor: colors.border,;
borderRadius: borderRadius.md,;
marginRight: spacing.sm,;
marginBottom: spacing.sm,;
}
    const backgroundColor = colors.surface;}
  }
selectedSpecialty: {,';,}borderColor: colors.primary,';'';
}
    const backgroundColor = colors.primary + '10';'}'';'';
  }
specialtyOptionText: {marginLeft: spacing.xs,;
fontSize: typography.sizes.sm,;
}
    const color = colors.textSecondary;}
  }
selectedSpecialtyText: {,;}}
    const color = colors.primary;}
  },';,'';
addCredentialButton: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'center';','';
paddingVertical: spacing.md,;
borderWidth: 2,';,'';
borderColor: colors.border,';,'';
borderStyle: 'dashed';','';
borderRadius: borderRadius.md,;
backgroundColor: colors.surface,;
}
    const marginBottom = spacing.md;}
  }
addCredentialText: {marginLeft: spacing.sm,;
fontSize: typography.sizes.md,;
}
    const color = colors.primary;}
  }
credentialItem: {backgroundColor: colors.surface,;
borderRadius: borderRadius.md,;
padding: spacing.md,;
marginBottom: spacing.md,;
borderWidth: 1,;
}
    const borderColor = colors.border;}
  },';,'';
credentialHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    const marginBottom = spacing.md;}
  }
credentialTitle: {fontSize: typography.sizes.md,;
fontWeight: typography.weights.medium,;
}
    const color = colors.text;}
  }
applyContent: {flex: 1,;
}
    const padding = spacing.md;}
  }
levelSection: {,;}}
    const marginBottom = spacing.xl;}
  }
levelSectionTitle: {fontSize: typography.sizes.lg,;
fontWeight: typography.weights.semibold,;
color: colors.text,;
}
    const marginBottom = spacing.md;}
  }
levelCard: {backgroundColor: colors.surface,;
borderRadius: borderRadius.md,;
padding: spacing.md,;
marginBottom: spacing.md,;
borderWidth: 1,;
}
    const borderColor = colors.border;}
  },';,'';
levelHeader: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = spacing.sm;}
  }
levelIcon: {width: 32,;
height: 32,';,'';
borderRadius: 16,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const marginRight = spacing.sm;}
  }
levelName: {fontSize: typography.sizes.md,;
fontWeight: typography.weights.medium,;
}
    const color = colors.text;}
  }
levelRequirements: {,;}}
    const marginLeft = spacing.xl;}
  }
requirementText: {fontSize: typography.sizes.sm,;
color: colors.textSecondary,;
marginBottom: spacing.xs,;
}
    const lineHeight = 18;}
  },';,'';
applyButton: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'center';','';
backgroundColor: colors.primary,;
paddingVertical: spacing.md,;
borderRadius: borderRadius.md,;
}
    const marginTop = spacing.md;}
  }
applyButtonText: {marginLeft: spacing.sm,;
fontSize: typography.sizes.md,';,'';
fontWeight: typography.weights.medium,';'';
}
    const color = 'white';'}'';'';
  }
expertDetailContainer: {flex: 1,;
}
    const padding = spacing.md;}
  },';,'';
expertDetailHeader: {,';,}flexDirection: 'row';','';'';
}
    const marginBottom = spacing.xl;}
  }
expertDetailAvatar: {width: 80,;
height: 80,;
borderRadius: 40,';,'';
backgroundColor: colors.background,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const marginRight = spacing.md;}
  }
detailAvatarImage: {width: 80,;
height: 80,;
}
    const borderRadius = 40;}
  }
expertDetailInfo: {,;}}
    const flex = 1;}
  }
expertDetailName: {fontSize: typography.sizes.xl,;
fontWeight: typography.weights.bold,;
color: colors.text,;
}
    const marginBottom = spacing.xs;}
  }
expertDetailTitle: {fontSize: typography.sizes.md,;
color: colors.text,;
}
    const marginBottom = spacing.xs;}
  }
expertDetailInstitution: {fontSize: typography.sizes.sm,;
color: colors.textSecondary,;
}
    const marginBottom = spacing.sm;}
  },';,'';
verificationInfo: {,';,}flexDirection: 'row';','';'';
}
    const alignItems = 'center';'}'';'';
  }
credibilityScore: {fontSize: typography.sizes.sm,;
color: colors.textSecondary,;
}
    const marginLeft = spacing.sm;}
  }
detailSection: {,;}}
    const marginBottom = spacing.xl;}
  }
detailSectionTitle: {fontSize: typography.sizes.lg,;
fontWeight: typography.weights.semibold,;
color: colors.text,;
}
    const marginBottom = spacing.md;}
  }
bioText: {fontSize: typography.sizes.md,;
color: colors.text,;
}
    const lineHeight = 24;}
  },';,'';
metricsGrid: {,';,}flexDirection: 'row';','';
flexWrap: 'wrap';','';'';
}
    const justifyContent = 'space-between';'}'';'';
  },';,'';
metricCard: {,';,}width: '48%';','';
backgroundColor: colors.surface,;
borderRadius: borderRadius.md,';,'';
padding: spacing.md,';,'';
alignItems: 'center';','';
marginBottom: spacing.sm,;
borderWidth: 1,;
}
    const borderColor = colors.border;}
  }
metricCardValue: {fontSize: typography.sizes.xl,;
fontWeight: typography.weights.bold,;
color: colors.primary,;
}
    const marginBottom = spacing.xs;}
  }
metricCardLabel: {fontSize: typography.sizes.sm,';,'';
color: colors.textSecondary,';'';
}
    const textAlign = 'center';'}'';'';
  },';,'';
credentialCard: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
backgroundColor: colors.surface,;
borderRadius: borderRadius.md,;
padding: spacing.md,;
marginBottom: spacing.sm,;
borderWidth: 1,;
}
    const borderColor = colors.border;}
  }
credentialInfo: {,;}}
    const flex = 1;}
  }
credentialCardTitle: {fontSize: typography.sizes.md,;
fontWeight: typography.weights.medium,;
color: colors.text,;
}
    const marginBottom = spacing.xs;}
  }
credentialInstitution: {fontSize: typography.sizes.sm,;
color: colors.textSecondary,;
}
    const marginBottom = spacing.xs;}
  }
credentialYear: {fontSize: typography.sizes.sm,;
}
    const color = colors.textSecondary;}
  }
credentialStatus: {width: 24,;
height: 24,';,'';
borderRadius: 12,';,'';
justifyContent: 'center';',')';'';
}
    const alignItems = 'center';')}'';'';
  },);
});
';,'';
export default ExpertVerificationSystem; ''';