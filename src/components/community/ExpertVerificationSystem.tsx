import React, { useCallback, useEffect, useState } from 'react';
import {
    ActivityIndicator,
    Alert,
    Dimensions,
    Image,
    Modal,
    ScrollView,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { borderRadius, colors, spacing, typography } from '../../constants/theme';

const { width } = Dimensions.get('window');

interface ExpertProfile {
  id: string;
  userId: string;
  name: string;
  avatar?: string;
  title: string;
  institution: string;
  specialties: string[];
  credentials: ExpertCredential[];
  verificationStatus: 'pending' | 'verified' | 'rejected' | 'suspended';
  verificationLevel: 'junior' | 'senior' | 'authority';
  credibilityScore: number;
  metrics: ExpertMetrics;
  bio: string;
  contactInfo: ContactInfo;
  createdAt: string;
  verifiedAt?: string;
}

interface ExpertCredential {
  id: string;
  type: 'education' | 'certification' | 'license' | 'publication' | 'award';
  title: string;
  institution: string;
  year: number;
  documentUrl?: string;
  verificationStatus: 'pending' | 'verified' | 'rejected';
}

interface ExpertMetrics {
  answersCount: number;
  helpfulAnswers: number;
  answerAcceptanceRate: number;
  averageRating: number;
  knowledgeContributions: number;
  peerEndorsements: number;
  consultationHours: number;
  patientSatisfaction: number;
}

interface ContactInfo {
  email: string;
  phone?: string;
  website?: string;
  socialMedia?: Record<string; string>;
}

interface ExpertVerificationSystemProps {
  currentUser?: any;
  onExpertVerified?: (expert: ExpertProfile) => void;
  onApplicationSubmitted?: (application: any) => void;
}

const ExpertVerificationSystem: React.FC<ExpertVerificationSystemProps> = ({
  currentUser,
  onExpertVerified,
  onApplicationSubmitted
;}) => {
  const [activeTab, setActiveTab] = useState<'apply' | 'experts' | 'manage'>('experts');
  const [experts, setExperts] = useState<ExpertProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedExpert, setSelectedExpert] = useState<ExpertProfile | null>(null);
  const [showExpertDetail, setShowExpertDetail] = useState(false);
  const [showApplicationForm, setShowApplicationForm] = useState(false);

  // 专家申请表单状态
  const [applicationForm, setApplicationForm] = useState({
    name: '';
    title: '';
    institution: '';
    specialties: [] as string[];
    bio: '';
    email: '';
    phone: '';
    credentials: [] as Partial<ExpertCredential>[]
  ;});

  // 专业领域配置
  const specialtyOptions = [












  ];

  // 认证等级配置
  const verificationLevels = {
    junior: {

      color: colors.info;
      icon: 'star-outline';

    },
    senior: {

      color: colors.warning;
      icon: 'star-half-full';

    },
    authority: {

      color: colors.success;
      icon: 'star';

    }
  };

  useEffect(() => {
    loadExperts();
  }, []);

  const loadExperts = useCallback(async () => {
    setLoading(true);
    try {
      // 模拟API调用
      const mockExperts: ExpertProfile[] = [
        {
          id: '1';
          userId: 'user_1';

          avatar: 'https://example.com/avatar1.jpg';


          specialties: ['tcm_internal', 'herbal_medicine'],
          credentials: [
            {
              id: '1';
              type: 'education';


              year: 2005;
              verificationStatus: 'verified'
            ;}
          ],
          verificationStatus: 'verified';
          verificationLevel: 'authority';
          credibilityScore: 0.95;
          metrics: {
            answersCount: 156;
            helpfulAnswers: 142;
            answerAcceptanceRate: 0.91;
            averageRating: 4.8;
            knowledgeContributions: 23;
            peerEndorsements: 45;
            consultationHours: 320;
            patientSatisfaction: 0.94
          ;},

          contactInfo: {
            email: 'wang.prof@example.com';
            website: 'https://wang-tcm.com'
          ;},
          createdAt: '2023-01-15';
          verifiedAt: '2023-02-01'
        ;},
        {
          id: '2';
          userId: 'user_2';



          specialties: ['acupuncture', 'rehabilitation'],
          credentials: [];
          verificationStatus: 'verified';
          verificationLevel: 'senior';
          credibilityScore: 0.88;
          metrics: {
            answersCount: 89;
            helpfulAnswers: 76;
            answerAcceptanceRate: 0.85;
            averageRating: 4.6;
            knowledgeContributions: 15;
            peerEndorsements: 28;
            consultationHours: 180;
            patientSatisfaction: 0.89
          ;},

          contactInfo: {
            email: 'li.doctor@example.com'
          ;},
          createdAt: '2023-03-10';
          verifiedAt: '2023-03-25'
        ;}
      ];
      setExperts(mockExperts);
    } catch (error) {

    } finally {
      setLoading(false);
    }
  }, []);

  const handleSubmitApplication = useCallback(async () => {
    if (!applicationForm.name || !applicationForm.title || !applicationForm.institution) {

      return;
    }

    if (applicationForm.specialties.length === 0) {

      return;
    }

    if (applicationForm.credentials.length === 0) {

      return;
    }

    try {
      setLoading(true);
      // 模拟提交申请
      await new Promise(resolve => setTimeout(resolve, 2000));
      

      setShowApplicationForm(false);
      setApplicationForm({
        name: '';
        title: '';
        institution: '';
        specialties: [];
        bio: '';
        email: '';
        phone: '';
        credentials: []
      ;});
      
      onApplicationSubmitted?.(applicationForm);
    } catch (error) {

    } finally {
      setLoading(false);
    }
  }, [applicationForm, onApplicationSubmitted]);

  const renderExpertCard = (expert: ExpertProfile) => {
    const levelConfig = verificationLevels[expert.verificationLevel];
    
    return (
      <TouchableOpacity
        key={expert.id}
        style={styles.expertCard}
        onPress={() => {
          setSelectedExpert(expert);
          setShowExpertDetail(true);
        }}
      >
        <View style={styles.expertHeader}>
          <View style={styles.expertAvatar}>
            {expert.avatar ? (
              <Image source={{ uri: expert.avatar ;}} style={styles.avatarImage} />
            ) : (
              <Icon name="account" size={32} color={colors.textSecondary} />
            )}
          </View>
          
          <View style={styles.expertInfo}>
            <View style={styles.expertNameRow}>
              <Text style={styles.expertName}>{expert.name}</Text>
              <View style={[styles.verificationBadge, { backgroundColor: levelConfig.color ;}]}>
                <Icon name={levelConfig.icon} size={12} color="white" />
                <Text style={styles.verificationText}>{levelConfig.name}</Text>
              </View>
            </View>
            
            <Text style={styles.expertTitle}>{expert.title}</Text>
            <Text style={styles.expertInstitution}>{expert.institution}</Text>
            
            <View style={styles.specialtyTags}>
              {expert.specialties.slice(0, 2).map(specialtyId => {
                const specialty = specialtyOptions.find(s => s.id === specialtyId);
                return specialty ? (
                  <View key={specialtyId} style={styles.specialtyTag}>
                    <Text style={styles.specialtyTagText}>{specialty.name}</Text>
                  </View>
                ) : null;
              })}
              {expert.specialties.length > 2 && (
                <Text style={styles.moreSpecialties}>+{expert.specialties.length - 2}</Text>
              )}
            </View>
          </View>
        </View>
        
        <View style={styles.expertMetrics}>
          <View style={styles.metricItem}>
            <Text style={styles.metricValue}>{expert.metrics.answersCount}</Text>
            <Text style={styles.metricLabel}>回答</Text>
          </View>
          <View style={styles.metricItem}>
            <Text style={styles.metricValue}>{expert.metrics.averageRating.toFixed(1)}</Text>
            <Text style={styles.metricLabel}>评分</Text>
          </View>
          <View style={styles.metricItem}>
            <Text style={styles.metricValue}>{(expert.credibilityScore * 100).toFixed(0)}%</Text>
            <Text style={styles.metricLabel}>可信度</Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  const renderApplicationForm = () => (
    <Modal
      visible={showApplicationForm}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={() => setShowApplicationForm(false)}
    >
      <SafeAreaView style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <TouchableOpacity onPress={() => setShowApplicationForm(false)}>
            <Icon name="close" size={24} color={colors.text} />
          </TouchableOpacity>
          <Text style={styles.modalTitle}>专家认证申请</Text>
          <TouchableOpacity onPress={handleSubmitApplication} disabled={loading}>
            <Text style={[styles.submitButton, loading && styles.disabledButton]}>

            </Text>
          </TouchableOpacity>
        </View>
        
        <ScrollView style={styles.formContainer}>
          {/* 基本信息 */}
          <View style={styles.formSection}>
            <Text style={styles.sectionTitle}>基本信息</Text>
            
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>姓名 *</Text>
              <TextInput
                style={styles.textInput}

                value={applicationForm.name}
                onChangeText={(text) => setApplicationForm(prev => ({ ...prev, name: text ;}))}
              />
            </View>
            
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>职称 *</Text>
              <TextInput
                style={styles.textInput}

                value={applicationForm.title}
                onChangeText={(text) => setApplicationForm(prev => ({ ...prev, title: text ;}))}
              />
            </View>
            
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>所属机构 *</Text>
              <TextInput
                style={styles.textInput}

                value={applicationForm.institution}
                onChangeText={(text) => setApplicationForm(prev => ({ ...prev, institution: text ;}))}
              />
            </View>
            
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>个人简介</Text>
              <TextInput
                style={[styles.textInput, styles.textArea]}

                value={applicationForm.bio}
                onChangeText={(text) => setApplicationForm(prev => ({ ...prev, bio: text ;}))}
                multiline
                textAlignVertical="top"
              />
            </View>
          </View>
          
          {/* 专业领域 */}
          <View style={styles.formSection}>
            <Text style={styles.sectionTitle}>专业领域 *</Text>
            <View style={styles.specialtyGrid}>
              {specialtyOptions.map(specialty => (
                <TouchableOpacity
                  key={specialty.id}
                  style={[
                    styles.specialtyOption,
                    applicationForm.specialties.includes(specialty.id) && styles.selectedSpecialty
                  ]}
                  onPress={() => {
                    setApplicationForm(prev => ({
                      ...prev,
                      specialties: prev.specialties.includes(specialty.id)
                        ? prev.specialties.filter(s => s !== specialty.id)
                        : [...prev.specialties, specialty.id]
                    ;}));
                  }}
                >
                  <Icon 
                    name={specialty.icon} 
                    size={20} 
                    color={applicationForm.specialties.includes(specialty.id) ? colors.primary : colors.textSecondary} 
                  />
                  <Text style={[
                    styles.specialtyOptionText,
                    applicationForm.specialties.includes(specialty.id) && styles.selectedSpecialtyText
                  ]}>
                    {specialty.name}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
          
          {/* 联系方式 */}
          <View style={styles.formSection}>
            <Text style={styles.sectionTitle}>联系方式</Text>
            
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>邮箱 *</Text>
              <TextInput
                style={styles.textInput}

                value={applicationForm.email}
                onChangeText={(text) => setApplicationForm(prev => ({ ...prev, email: text ;}))}
                keyboardType="email-address"
              />
            </View>
            
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>电话</Text>
              <TextInput
                style={styles.textInput}

                value={applicationForm.phone}
                onChangeText={(text) => setApplicationForm(prev => ({ ...prev, phone: text ;}))}
                keyboardType="phone-pad"
              />
            </View>
          </View>
          
          {/* 资质证明 */}
          <View style={styles.formSection}>
            <Text style={styles.sectionTitle}>资质证明 *</Text>
            <Text style={styles.sectionDescription}>

            </Text>
            
            <TouchableOpacity
              style={styles.addCredentialButton}
              onPress={() => {
                setApplicationForm(prev => ({
                  ...prev,
                  credentials: [...prev.credentials, {
                    type: 'education';
                    title: '';
                    institution: '';
                    year: new Date().getFullYear()
                  ;}]
                }));
              }}
            >
              <Icon name="plus" size={20} color={colors.primary} />
              <Text style={styles.addCredentialText}>添加资质证明</Text>
            </TouchableOpacity>
            
            {applicationForm.credentials.map((credential, index) => (
              <View key={index} style={styles.credentialItem}>
                <View style={styles.credentialHeader}>
                  <Text style={styles.credentialTitle}>证明 {index + 1}</Text>
                  <TouchableOpacity
                    onPress={() => {
                      setApplicationForm(prev => ({
                        ...prev,
                        credentials: prev.credentials.filter((_, i) => i !== index)
                      ;}));
                    }}
                  >
                    <Icon name="delete" size={20} color={colors.error} />
                  </TouchableOpacity>
                </View>
                
                <TextInput
                  style={styles.textInput}

                  value={credential.title}
                  onChangeText={(text) => {
                    setApplicationForm(prev => ({
                      ...prev,
                      credentials: prev.credentials.map((c, i) => 
                        i === index ? { ...c, title: text ;} : c
                      )
                    }));
                  }}
                />
                
                <TextInput
                  style={styles.textInput}

                  value={credential.institution}
                  onChangeText={(text) => {
                    setApplicationForm(prev => ({
                      ...prev,
                      credentials: prev.credentials.map((c, i) => 
                        i === index ? { ...c, institution: text ;} : c
                      )
                    }));
                  }}
                />
              </View>
            ))}
          </View>
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );

  const renderExpertDetail = () => (
    <Modal
      visible={showExpertDetail}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={() => setShowExpertDetail(false)}
    >
      <SafeAreaView style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <TouchableOpacity onPress={() => setShowExpertDetail(false)}>
            <Icon name="arrow-left" size={24} color={colors.text} />
          </TouchableOpacity>
          <Text style={styles.modalTitle}>专家详情</Text>
          <View style={{ width: 24 ;}} />
        </View>
        
        {selectedExpert && (
          <ScrollView style={styles.expertDetailContainer}>
            {/* 专家基本信息 */}
            <View style={styles.expertDetailHeader}>
              <View style={styles.expertDetailAvatar}>
                {selectedExpert.avatar ? (
                  <Image source={{ uri: selectedExpert.avatar ;}} style={styles.detailAvatarImage} />
                ) : (
                  <Icon name="account" size={48} color={colors.textSecondary} />
                )}
              </View>
              
              <View style={styles.expertDetailInfo}>
                <Text style={styles.expertDetailName}>{selectedExpert.name}</Text>
                <Text style={styles.expertDetailTitle}>{selectedExpert.title}</Text>
                <Text style={styles.expertDetailInstitution}>{selectedExpert.institution}</Text>
                
                <View style={styles.verificationInfo}>
                  <View style={[
                    styles.verificationBadge, 
                    { backgroundColor: verificationLevels[selectedExpert.verificationLevel].color ;}
                  ]}>
                    <Icon 
                      name={verificationLevels[selectedExpert.verificationLevel].icon} 
                      size={12} 
                      color="white" 
                    />
                    <Text style={styles.verificationText}>
                      {verificationLevels[selectedExpert.verificationLevel].name}
                    </Text>
                  </View>
                  <Text style={styles.credibilityScore}>
                    可信度: {(selectedExpert.credibilityScore * 100).toFixed(0)}%
                  </Text>
                </View>
              </View>
            </View>
            
            {/* 专业领域 */}
            <View style={styles.detailSection}>
              <Text style={styles.detailSectionTitle}>专业领域</Text>
              <View style={styles.specialtyTags}>
                {selectedExpert.specialties.map(specialtyId => {
                  const specialty = specialtyOptions.find(s => s.id === specialtyId);
                  return specialty ? (
                    <View key={specialtyId} style={styles.specialtyTag}>
                      <Icon name={specialty.icon} size={14} color={colors.primary} />
                      <Text style={styles.specialtyTagText}>{specialty.name}</Text>
                    </View>
                  ) : null;
                })}
              </View>
            </View>
            
            {/* 个人简介 */}
            <View style={styles.detailSection}>
              <Text style={styles.detailSectionTitle}>个人简介</Text>
              <Text style={styles.bioText}>{selectedExpert.bio}</Text>
            </View>
            
            {/* 专业数据 */}
            <View style={styles.detailSection}>
              <Text style={styles.detailSectionTitle}>专业数据</Text>
              <View style={styles.metricsGrid}>
                <View style={styles.metricCard}>
                  <Text style={styles.metricCardValue}>{selectedExpert.metrics.answersCount}</Text>
                  <Text style={styles.metricCardLabel}>回答数量</Text>
                </View>
                <View style={styles.metricCard}>
                  <Text style={styles.metricCardValue}>{selectedExpert.metrics.averageRating.toFixed(1)}</Text>
                  <Text style={styles.metricCardLabel}>平均评分</Text>
                </View>
                <View style={styles.metricCard}>
                  <Text style={styles.metricCardValue}>{(selectedExpert.metrics.answerAcceptanceRate * 100).toFixed(0)}%</Text>
                  <Text style={styles.metricCardLabel}>采纳率</Text>
                </View>
                <View style={styles.metricCard}>
                  <Text style={styles.metricCardValue}>{selectedExpert.metrics.consultationHours}</Text>
                  <Text style={styles.metricCardLabel}>咨询时长</Text>
                </View>
              </View>
            </View>
            
            {/* 资质证明 */}
            {selectedExpert.credentials.length > 0 && (
              <View style={styles.detailSection}>
                <Text style={styles.detailSectionTitle}>资质证明</Text>
                {selectedExpert.credentials.map(credential => (
                  <View key={credential.id} style={styles.credentialCard}>
                    <View style={styles.credentialInfo}>
                      <Text style={styles.credentialCardTitle}>{credential.title}</Text>
                      <Text style={styles.credentialInstitution}>{credential.institution}</Text>
                      <Text style={styles.credentialYear}>{credential.year}年</Text>
                    </View>
                    <View style={[
                      styles.credentialStatus,
                      { backgroundColor: credential.verificationStatus === 'verified' ? colors.success : colors.warning ;}
                    ]}>
                      <Icon 
                        name={credential.verificationStatus === 'verified' ? 'check' : 'clock'} 
                        size={12} 
                        color="white" 
                      />
                    </View>
                  </View>
                ))}
              </View>
            )}
          </ScrollView>
        )}
      </SafeAreaView>
    </Modal>
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* 标签页导航 */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'experts' && styles.activeTab]}
          onPress={() => setActiveTab('experts')}
        >
          <Icon 
            name="account-group" 
            size={20} 
            color={activeTab === 'experts' ? colors.primary : colors.textSecondary} 
          />
          <Text style={[styles.tabText, activeTab === 'experts' && styles.activeTabText]}>

          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, activeTab === 'apply' && styles.activeTab]}
          onPress={() => setActiveTab('apply')}
        >
          <Icon 
            name="account-plus" 
            size={20} 
            color={activeTab === 'apply' ? colors.primary : colors.textSecondary} 
          />
          <Text style={[styles.tabText, activeTab === 'apply' && styles.activeTabText]}>

          </Text>
        </TouchableOpacity>
      </View>
      
      {/* 内容区域 */}
      {activeTab === 'experts' && (
        <View style={styles.content}>
          <View style={styles.contentHeader}>
            <Text style={styles.contentTitle}>认证专家</Text>
            <Text style={styles.contentSubtitle}>

            </Text>
          </View>
          
          {loading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color={colors.primary} />
            </View>
          ) : (
            <ScrollView style={styles.expertsList}>
              {experts.map(renderExpertCard)}
            </ScrollView>
          )}
        </View>
      )}
      
      {activeTab === 'apply' && (
        <View style={styles.content}>
          <View style={styles.contentHeader}>
            <Text style={styles.contentTitle}>专家认证申请</Text>
            <Text style={styles.contentSubtitle}>

            </Text>
          </View>
          
          <ScrollView style={styles.applyContent}>
            {/* 认证等级说明 */}
            <View style={styles.levelSection}>
              <Text style={styles.levelSectionTitle}>认证等级</Text>
              {Object.entries(verificationLevels).map(([level, config]) => (
                <View key={level} style={styles.levelCard}>
                  <View style={styles.levelHeader}>
                    <View style={[styles.levelIcon, { backgroundColor: config.color ;}]}>
                      <Icon name={config.icon} size={20} color="white" />
                    </View>
                    <Text style={styles.levelName}>{config.name}</Text>
                  </View>
                  <View style={styles.levelRequirements}>
                    {config.requirements.map((requirement, index) => (
                      <Text key={index} style={styles.requirementText}>
                        • {requirement}
                      </Text>
                    ))}
                  </View>
                </View>
              ))}
            </View>
            
            {/* 申请按钮 */}
            <TouchableOpacity
              style={styles.applyButton}
              onPress={() => setShowApplicationForm(true)}
            >
              <Icon name="account-plus" size={20} color="white" />
              <Text style={styles.applyButtonText}>开始申请认证</Text>
            </TouchableOpacity>
          </ScrollView>
        </View>
      )}
      
      {renderApplicationForm()}
      {renderExpertDetail()}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1;
    backgroundColor: colors.background;
  },
  tabContainer: {
    flexDirection: 'row';
    backgroundColor: colors.surface;
    borderBottomWidth: 1;
    borderBottomColor: colors.border;
  },
  tab: {
    flex: 1;
    flexDirection: 'row';
    alignItems: 'center';
    justifyContent: 'center';
    paddingVertical: spacing.md;
    paddingHorizontal: spacing.sm;
  },
  activeTab: {
    borderBottomWidth: 2;
    borderBottomColor: colors.primary;
  },
  tabText: {
    marginLeft: spacing.xs;
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
  },
  activeTabText: {
    color: colors.primary;
    fontWeight: typography.weights.medium;
  },
  content: {
    flex: 1;
  },
  contentHeader: {
    padding: spacing.md;
    backgroundColor: colors.surface;
  },
  contentTitle: {
    fontSize: typography.sizes.xl;
    fontWeight: typography.weights.bold;
    color: colors.text;
    marginBottom: spacing.xs;
  },
  contentSubtitle: {
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
    lineHeight: 20;
  },
  loadingContainer: {
    flex: 1;
    justifyContent: 'center';
    alignItems: 'center';
  },
  expertsList: {
    flex: 1;
    padding: spacing.md;
  },
  expertCard: {
    backgroundColor: colors.surface;
    borderRadius: borderRadius.lg;
    padding: spacing.md;
    marginBottom: spacing.md;
    borderWidth: 1;
    borderColor: colors.border;
  },
  expertHeader: {
    flexDirection: 'row';
    marginBottom: spacing.md;
  },
  expertAvatar: {
    width: 60;
    height: 60;
    borderRadius: 30;
    backgroundColor: colors.background;
    justifyContent: 'center';
    alignItems: 'center';
    marginRight: spacing.md;
  },
  avatarImage: {
    width: 60;
    height: 60;
    borderRadius: 30;
  },
  expertInfo: {
    flex: 1;
  },
  expertNameRow: {
    flexDirection: 'row';
    alignItems: 'center';
    marginBottom: spacing.xs;
  },
  expertName: {
    fontSize: typography.sizes.lg;
    fontWeight: typography.weights.semibold;
    color: colors.text;
    marginRight: spacing.sm;
  },
  verificationBadge: {
    flexDirection: 'row';
    alignItems: 'center';
    paddingHorizontal: spacing.xs;
    paddingVertical: 2;
    borderRadius: borderRadius.sm;
  },
  verificationText: {
    fontSize: typography.sizes.xs;
    color: 'white';
    marginLeft: 2;
  },
  expertTitle: {
    fontSize: typography.sizes.md;
    color: colors.text;
    marginBottom: spacing.xs;
  },
  expertInstitution: {
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
    marginBottom: spacing.sm;
  },
  specialtyTags: {
    flexDirection: 'row';
    flexWrap: 'wrap';
    alignItems: 'center';
  },
  specialtyTag: {
    flexDirection: 'row';
    alignItems: 'center';
    backgroundColor: colors.primary + '20';
    paddingHorizontal: spacing.xs;
    paddingVertical: 2;
    borderRadius: borderRadius.sm;
    marginRight: spacing.xs;
    marginBottom: spacing.xs;
  },
  specialtyTagText: {
    fontSize: typography.sizes.xs;
    color: colors.primary;
    marginLeft: 2;
  },
  moreSpecialties: {
    fontSize: typography.sizes.xs;
    color: colors.textSecondary;
  },
  expertMetrics: {
    flexDirection: 'row';
    justifyContent: 'space-around';
    paddingTop: spacing.md;
    borderTopWidth: 1;
    borderTopColor: colors.border;
  },
  metricItem: {
    alignItems: 'center';
  },
  metricValue: {
    fontSize: typography.sizes.lg;
    fontWeight: typography.weights.semibold;
    color: colors.primary;
  },
  metricLabel: {
    fontSize: typography.sizes.xs;
    color: colors.textSecondary;
    marginTop: spacing.xs;
  },
  modalContainer: {
    flex: 1;
    backgroundColor: colors.background;
  },
  modalHeader: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    paddingHorizontal: spacing.md;
    paddingVertical: spacing.md;
    borderBottomWidth: 1;
    borderBottomColor: colors.border;
  },
  modalTitle: {
    fontSize: typography.sizes.lg;
    fontWeight: typography.weights.semibold;
    color: colors.text;
  },
  submitButton: {
    color: colors.primary;
    fontSize: typography.sizes.sm;
    fontWeight: typography.weights.medium;
  },
  disabledButton: {
    color: colors.textSecondary;
  },
  formContainer: {
    flex: 1;
    padding: spacing.md;
  },
  formSection: {
    marginBottom: spacing.xl;
  },
  sectionTitle: {
    fontSize: typography.sizes.lg;
    fontWeight: typography.weights.semibold;
    color: colors.text;
    marginBottom: spacing.md;
  },
  sectionDescription: {
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
    marginBottom: spacing.md;
    lineHeight: 20;
  },
  inputGroup: {
    marginBottom: spacing.md;
  },
  inputLabel: {
    fontSize: typography.sizes.md;
    fontWeight: typography.weights.medium;
    color: colors.text;
    marginBottom: spacing.sm;
  },
  textInput: {
    borderWidth: 1;
    borderColor: colors.border;
    borderRadius: borderRadius.md;
    paddingHorizontal: spacing.md;
    paddingVertical: spacing.sm;
    fontSize: typography.sizes.md;
    color: colors.text;
    backgroundColor: colors.surface;
  },
  textArea: {
    minHeight: 100;
    textAlignVertical: 'top';
  },
  specialtyGrid: {
    flexDirection: 'row';
    flexWrap: 'wrap';
  },
  specialtyOption: {
    flexDirection: 'row';
    alignItems: 'center';
    paddingHorizontal: spacing.md;
    paddingVertical: spacing.sm;
    borderWidth: 1;
    borderColor: colors.border;
    borderRadius: borderRadius.md;
    marginRight: spacing.sm;
    marginBottom: spacing.sm;
    backgroundColor: colors.surface;
  },
  selectedSpecialty: {
    borderColor: colors.primary;
    backgroundColor: colors.primary + '10';
  },
  specialtyOptionText: {
    marginLeft: spacing.xs;
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
  },
  selectedSpecialtyText: {
    color: colors.primary;
  },
  addCredentialButton: {
    flexDirection: 'row';
    alignItems: 'center';
    justifyContent: 'center';
    paddingVertical: spacing.md;
    borderWidth: 2;
    borderColor: colors.border;
    borderStyle: 'dashed';
    borderRadius: borderRadius.md;
    backgroundColor: colors.surface;
    marginBottom: spacing.md;
  },
  addCredentialText: {
    marginLeft: spacing.sm;
    fontSize: typography.sizes.md;
    color: colors.primary;
  },
  credentialItem: {
    backgroundColor: colors.surface;
    borderRadius: borderRadius.md;
    padding: spacing.md;
    marginBottom: spacing.md;
    borderWidth: 1;
    borderColor: colors.border;
  },
  credentialHeader: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    marginBottom: spacing.md;
  },
  credentialTitle: {
    fontSize: typography.sizes.md;
    fontWeight: typography.weights.medium;
    color: colors.text;
  },
  applyContent: {
    flex: 1;
    padding: spacing.md;
  },
  levelSection: {
    marginBottom: spacing.xl;
  },
  levelSectionTitle: {
    fontSize: typography.sizes.lg;
    fontWeight: typography.weights.semibold;
    color: colors.text;
    marginBottom: spacing.md;
  },
  levelCard: {
    backgroundColor: colors.surface;
    borderRadius: borderRadius.md;
    padding: spacing.md;
    marginBottom: spacing.md;
    borderWidth: 1;
    borderColor: colors.border;
  },
  levelHeader: {
    flexDirection: 'row';
    alignItems: 'center';
    marginBottom: spacing.sm;
  },
  levelIcon: {
    width: 32;
    height: 32;
    borderRadius: 16;
    justifyContent: 'center';
    alignItems: 'center';
    marginRight: spacing.sm;
  },
  levelName: {
    fontSize: typography.sizes.md;
    fontWeight: typography.weights.medium;
    color: colors.text;
  },
  levelRequirements: {
    marginLeft: spacing.xl;
  },
  requirementText: {
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
    marginBottom: spacing.xs;
    lineHeight: 18;
  },
  applyButton: {
    flexDirection: 'row';
    alignItems: 'center';
    justifyContent: 'center';
    backgroundColor: colors.primary;
    paddingVertical: spacing.md;
    borderRadius: borderRadius.md;
    marginTop: spacing.md;
  },
  applyButtonText: {
    marginLeft: spacing.sm;
    fontSize: typography.sizes.md;
    fontWeight: typography.weights.medium;
    color: 'white';
  },
  expertDetailContainer: {
    flex: 1;
    padding: spacing.md;
  },
  expertDetailHeader: {
    flexDirection: 'row';
    marginBottom: spacing.xl;
  },
  expertDetailAvatar: {
    width: 80;
    height: 80;
    borderRadius: 40;
    backgroundColor: colors.background;
    justifyContent: 'center';
    alignItems: 'center';
    marginRight: spacing.md;
  },
  detailAvatarImage: {
    width: 80;
    height: 80;
    borderRadius: 40;
  },
  expertDetailInfo: {
    flex: 1;
  },
  expertDetailName: {
    fontSize: typography.sizes.xl;
    fontWeight: typography.weights.bold;
    color: colors.text;
    marginBottom: spacing.xs;
  },
  expertDetailTitle: {
    fontSize: typography.sizes.md;
    color: colors.text;
    marginBottom: spacing.xs;
  },
  expertDetailInstitution: {
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
    marginBottom: spacing.sm;
  },
  verificationInfo: {
    flexDirection: 'row';
    alignItems: 'center';
  },
  credibilityScore: {
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
    marginLeft: spacing.sm;
  },
  detailSection: {
    marginBottom: spacing.xl;
  },
  detailSectionTitle: {
    fontSize: typography.sizes.lg;
    fontWeight: typography.weights.semibold;
    color: colors.text;
    marginBottom: spacing.md;
  },
  bioText: {
    fontSize: typography.sizes.md;
    color: colors.text;
    lineHeight: 24;
  },
  metricsGrid: {
    flexDirection: 'row';
    flexWrap: 'wrap';
    justifyContent: 'space-between';
  },
  metricCard: {
    width: '48%';
    backgroundColor: colors.surface;
    borderRadius: borderRadius.md;
    padding: spacing.md;
    alignItems: 'center';
    marginBottom: spacing.sm;
    borderWidth: 1;
    borderColor: colors.border;
  },
  metricCardValue: {
    fontSize: typography.sizes.xl;
    fontWeight: typography.weights.bold;
    color: colors.primary;
    marginBottom: spacing.xs;
  },
  metricCardLabel: {
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
    textAlign: 'center';
  },
  credentialCard: {
    flexDirection: 'row';
    alignItems: 'center';
    backgroundColor: colors.surface;
    borderRadius: borderRadius.md;
    padding: spacing.md;
    marginBottom: spacing.sm;
    borderWidth: 1;
    borderColor: colors.border;
  },
  credentialInfo: {
    flex: 1;
  },
  credentialCardTitle: {
    fontSize: typography.sizes.md;
    fontWeight: typography.weights.medium;
    color: colors.text;
    marginBottom: spacing.xs;
  },
  credentialInstitution: {
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
    marginBottom: spacing.xs;
  },
  credentialYear: {
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
  },
  credentialStatus: {
    width: 24;
    height: 24;
    borderRadius: 12;
    justifyContent: 'center';
    alignItems: 'center';
  },
});

export default ExpertVerificationSystem; 