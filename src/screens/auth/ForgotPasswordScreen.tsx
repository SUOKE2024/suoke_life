import { useNavigation } from "@react-navigation/native";""/;,"/g"/;
import { NativeStackNavigationProp } from "@react-navigation/native-stack";""/;,"/g"/;
import React, { useState } from "react";";
import {;,}Alert,;
KeyboardAvoidingView,;
Platform,;
ScrollView,;
StyleSheet,;
Text,;
TextInput,;
TouchableOpacity,";"";
}
  View'}'';'';
} from "react-native";";
import { SafeAreaView } from "react-native-safe-area-context";";
const type = AuthStackParamList = {Welcome: undefined}Login: undefined,;
Register: undefined,;
}
  const ForgotPassword = undefined;}
};
const type = ForgotPasswordScreenNavigationProp = NativeStackNavigationProp<";,"";
AuthStackParamList,';'';
  'ForgotPassword'';'';
>;
const  ForgotPasswordScreen: React.FC = () => {}';,'';
const navigation = useNavigation<Suspense fallback={<LoadingSpinner  />}><ForgotPasswordScreenNavigationProp></Suspense>();'/;,'/g'/;
const [email, setEmail] = useState(');'';
const [loading, setLoading] = useState(false);';,'';
const [emailSent, setEmailSent] = useState(false);';,'';
const [error, setError] = useState(');'';
const  validateEmail = useCallback((email: string) => {const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;/;}}/g/;
    return emailRegex.test(email);}
  };
const  handleSendResetEmail = async () => {if (!email.trim()) {}}
      return;}
    }

    if (!validateEmail(email)) {}}
      return;}
    }';'';
';,'';
setError(');'';
setLoading(true);
try {// TODO: 实现实际的重置密码逻辑/;,}await: new Promise(resolve => setTimeout(resolve, 2000)); // 模拟网络请求/;/g/;
}
      setEmailSent(true);}
    } catch (error) {}}
}
    } finally {}}
      setLoading(false);}
    }
  };
const  handleResendEmail = async () => {setLoading(true);,}try {await: new Promise(resolve => setTimeout(resolve, 1000));}}
}
    } catch (error) {}}
}
    } finally {}}
      setLoading(false);}
    }
  };
';,'';
const  handleBackToLogin = useCallback(() => {';}}'';
    navigation.navigate('Login');'}'';'';
  };
const  handleBack = useCallback(() => {}}
    navigation.goBack();}
  };
const  handleEmailChange = useCallback((value: string) => {setEmail(value);';,}if (error) {';}}'';
      setError(');'}'';'';
    }
  };
if (emailSent) {}
    return (<SafeAreaView style={styles.container}>;)        <ScrollView;  />/;,/g/;
style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >;
          <View style={styles.successContainer}>;
            <View style={styles.successIcon}>;
              <Text style={styles.successIconText}>✉️</Text>/;/g/;
            </View>/;/g/;
            <Text style={styles.successTitle}>邮件已发送</Text>/;/g/;
            <Text style={styles.successMessage}>;

            </Text>/;/g/;
            <View style={styles.actionButtons}>;
              <TouchableOpacity;  />/;,/g/;
style={[styles.button, styles.resendButton]}
                onPress={handleResendEmail}
                disabled={loading}
              >;
                <Text style={styles.buttonText}>;

                </Text>/;/g/;
              </TouchableOpacity>/;/g/;
              <TouchableOpacity;  />/;,/g/;
style={[styles.button, styles.backToLoginButton]}
                onPress={handleBackToLogin}
              >;
                <Text style={[styles.buttonText, styles.primaryButtonText]}>;

                </Text>/;/g/;
              </TouchableOpacity>/;/g/;
            </View>/;/g/;
            <View style={styles.helpSection}>;
              <Text style={styles.helpTitle}>需要帮助？</Text>/;/g/;
              <Text style={styles.helpText}>;

              </Text>/;/g/;
              <TouchableOpacity style={styles.contactButton}>;
                <Text style={styles.contactButtonText}>联系客服</Text>/;/g/;
              </TouchableOpacity>/;/g/;
            </View>/;/g/;
          </View>)/;/g/;
        </ScrollView>)/;/g/;
      </SafeAreaView>)/;/g/;
    );
  }

  return (<SafeAreaView style={styles.container}>;)      <KeyboardAvoidingView;'  />/;,'/g'/;
style={styles.keyboardAvoid}';,'';
behavior={Platform.OS === 'ios' ? 'padding' : 'height'}';'';
      >;
        <ScrollView;  />/;,/g/;
style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}';,'';
showsVerticalScrollIndicator={false}';,'';
keyboardShouldPersistTaps="handled"";"";
        >;
          <View style={styles.header}>;
            <TouchableOpacity style={styles.backButton} onPress={handleBack}>;
              <Text style={styles.backButtonText}>←</Text>/;/g/;
            </TouchableOpacity>/;/g/;
            <View style={styles.iconContainer}>;
              <View style={styles.iconPlaceholder}>;
                <Text style={styles.iconText}>🔑</Text>/;/g/;
              </View>/;/g/;
            </View>/;/g/;
            <Text style={styles.title}>忘记密码</Text>/;/g/;
            <Text style={styles.subtitle}>;

            </Text>/;/g/;
          </View>/;/g/;

          <View style={styles.formSection}>;
            <View style={styles.inputContainer}>;
              <Text style={styles.inputLabel}>邮箱地址</Text>/;/g/;
              <TextInput;  />/;,/g/;
style={[styles.input, error && styles.inputError]}
                value={email}
                onChangeText={handleEmailChange}";"";
";,"";
keyboardType="email-address";
autoCapitalize="none";
autoCorrect={false}
              />/;/g/;
              {error && <Text style={styles.errorText}>{error}</Text>}/;/g/;
            </View>/;/g/;
            <TouchableOpacity;  />/;,/g/;
style={[styles.button, styles.sendButton]}
              onPress={handleSendResetEmail}
              disabled={loading}
            >;
              <Text style={[styles.buttonText, styles.primaryButtonText]}>;

              </Text>/;/g/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;

          <View style={styles.securitySection}>;
            <Text style={styles.securityTitle}>安全提示</Text>/;/g/;
            <View style={styles.securityList}>;
              <View style={styles.securityItem}>;
                <Text style={styles.securityIcon}>🔒</Text>/;/g/;
                <Text style={styles.securityText}>;

                </Text>/;/g/;
              </View>/;/g/;
              <View style={styles.securityItem}>;
                <Text style={styles.securityIcon}>📧</Text>/;/g/;
                <Text style={styles.securityText}>邮件将从官方邮箱发送</Text>/;/g/;
              </View>/;/g/;
              <View style={styles.securityItem}>;
                <Text style={styles.securityIcon}>🛡️</Text>/;/g/;
                <Text style={styles.securityText}>;

                </Text>/;/g/;
              </View>/;/g/;
            </View>/;/g/;
          </View>/;/g/;

          <View style={styles.alternativeSection}>;
            <Text style={styles.alternativeText}>;

              <Text style={styles.loginLink} onPress={handleBackToLogin}>;

              </Text>/;/g/;
            </Text>/;/g/;
          </View>/;/g/;
        </ScrollView>)/;/g/;
      </KeyboardAvoidingView>)/;/g/;
    </SafeAreaView>)/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,";,}flex: 1,";"";
}
    const backgroundColor = '#F5F7FA'}'';'';
  ;}
keyboardAvoid: {,;}}
  const flex = 1}
  ;}
scrollView: {,;}}
  const flex = 1}
  ;}
scrollContent: {flexGrow: 1,;
}
    const paddingHorizontal = 20}
  ;},';,'';
header: {,';,}alignItems: 'center';','';
paddingTop: 20,;
}
    const paddingBottom = 40}
  ;},';,'';
backButton: {,';,}position: 'absolute';','';
left: 0,;
top: 20,;
width: 40,;
height: 40,';,'';
borderRadius: 20,';,'';
backgroundColor: '#E1E8ED';','';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
backButtonText: {,';,}fontSize: 20,';'';
}
    const color = '#2C3E50'}'';'';
  ;}
iconContainer: {,;}}
  const marginBottom = 20}
  ;}
iconPlaceholder: {width: 80,;
height: 80,';,'';
borderRadius: 40,';,'';
backgroundColor: '#3498DB';','';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
iconText: {,;}}
  const fontSize = 32}
  ;}
title: {,';,}fontSize: 28,';,'';
fontWeight: 'bold';','';
color: '#2C3E50';','';'';
}
    const marginBottom = 8}
  ;}
subtitle: {,';,}fontSize: 16,';,'';
color: '#7F8C8D';','';
textAlign: 'center';','';'';
}
    const lineHeight = 24}
  ;}
formSection: {,;}}
  const paddingVertical = 20}
  ;}
inputContainer: {,;}}
  const marginBottom = 24}
  ;}
inputLabel: {,';,}fontSize: 14,';,'';
color: '#7F8C8D';','';'';
}
    const marginBottom = 8}
  ;}
input: {,';,}borderWidth: 1,';,'';
borderColor: '#E1E8ED';','';
borderRadius: 8,;
paddingHorizontal: 16,';,'';
paddingVertical: 12,';,'';
backgroundColor: '#FFFFFF';','';
fontSize: 16,;
}
    const minHeight = 48}
  ;},';,'';
inputError: {,';}}'';
  const borderColor = '#E74C3C'}'';'';
  ;}
errorText: {,';,}fontSize: 14,';,'';
color: '#E74C3C';','';'';
}
    const marginTop = 4}
  ;}
button: {borderRadius: 8,;
paddingVertical: 16,';,'';
paddingHorizontal: 24,';,'';
alignItems: 'center';','';
justifyContent: 'center';','';'';
}
    const marginBottom = 16}
  ;}
buttonText: {,';,}fontSize: 16,';'';
}
    const fontWeight = '600'}'';'';
  ;},';,'';
sendButton: {,';}}'';
  const backgroundColor = '#3498DB'}'';'';
  ;},';,'';
primaryButtonText: {,';}}'';
  const color = '#FFFFFF'}'';'';
  ;},';,'';
securitySection: {,';,}backgroundColor: '#FFFFFF';','';
borderRadius: 12,;
padding: 20,;
}
    const marginVertical = 20}
  ;}
securityTitle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';
color: '#2C3E50';','';'';
}
    const marginBottom = 16}
  ;}
securityList: {,;}}
  const gap = 12}
  ;},';,'';
securityItem: {,';,}flexDirection: 'row';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
securityIcon: {fontSize: 18,;
}
    const marginRight = 12}
  ;}
securityText: {flex: 1,';,'';
fontSize: 14,';'';
}
    const color = '#7F8C8D'}'';'';
  ;},';,'';
alternativeSection: {,';,}alignItems: 'center';','';'';
}
    const paddingVertical = 24}
  ;}
alternativeText: {,';,}fontSize: 16,';'';
}
    const color = '#7F8C8D'}'';'';
  ;},';,'';
loginLink: {,';,}color: '#3498DB';','';'';
}
    const fontWeight = '600'}'';'';
  ;}
successContainer: {,';,}flex: 1,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const paddingVertical = 40}
  ;}
successIcon: {width: 120,;
height: 120,';,'';
borderRadius: 60,';,'';
backgroundColor: '#27AE60';','';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const marginBottom = 24}
  ;}
successIconText: {,;}}
  const fontSize = 48}
  ;}
successTitle: {,';,}fontSize: 28,';,'';
fontWeight: 'bold';','';
color: '#2C3E50';','';'';
}
    const marginBottom = 16}
  ;}
successMessage: {,';,}fontSize: 16,';,'';
color: '#7F8C8D';','';
textAlign: 'center';','';
lineHeight: 24,;
}
    const marginBottom = 32}
  ;},';,'';
actionButtons: {,';,}width: '100%';','';'';
}
    const marginBottom = 24}
  ;},';,'';
resendButton: {,';,}backgroundColor: '#FFFFFF';','';
borderWidth: 1,';'';
}
    const borderColor = '#3498DB'}'';'';
  ;},';,'';
backToLoginButton: {,';}}'';
  const backgroundColor = '#3498DB'}'';'';
  ;},';,'';
helpSection: {,';,}backgroundColor: '#FFFFFF';','';
borderRadius: 12,';,'';
padding: 20,';,'';
width: '100%';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
helpTitle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';
color: '#2C3E50';','';'';
}
    const marginBottom = 8}
  ;}
helpText: {,';,}fontSize: 14,';,'';
color: '#7F8C8D';','';
textAlign: 'center';','';'';
}
    const marginBottom = 16}
  ;}
contactButton: {paddingHorizontal: 20,;
paddingVertical: 8,;
borderRadius: 8,';,'';
borderWidth: 1,';'';
}
    const borderColor = '#3498DB'}'';'';
  ;}
contactButtonText: {,';,}fontSize: 14,';,'';
color: '#3498DB';',')';'';
}
    const fontWeight = '600')}'';'';
  ;});
});
export default ForgotPasswordScreen;';'';
''';