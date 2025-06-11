import { useNavigation } from "@react-navigation/native"
import React, { useEffect, useState } from "react";
import {ActivityIndicator,
Alert,
KeyboardAvoidingView,
Platform,
ScrollView,
StyleSheet,
Text,
TextInput,"
TouchableOpacity,";
} fromiew'}
} from "react-native;
import {  SafeAreaView  } from "react-native-safe-area-context"
import { unifiedApiService } from "../../services/unifiedApiService"
import { isLoggedIn } from "../../utils/authUtils"
interface LoginFormData {email: string}password: string,
}
}
  const rememberMe = boolean}
}
interface LoginFormErrors {
email?: stringpassword?: string;
}
  general?: string}
}
const  LoginScreen: React.FC = () => {const navigation = useNavigation();"const [formData, setFormData] = useState<LoginFormData>({',)email: ,')''password: ,)'
}
    const rememberMe = false)}
  ;});
const [errors, setErrors] = useState<LoginFormErrors>({});
const [loading, setLoading] = useState(false);
const [showPassword, setShowPassword] = useState(false);
  // 检查是否已登录
useEffect() => {}
    checkAuthStatus()}
  }, []);
const  checkAuthStatus = async () => {try {}      const loggedIn = await isLoggedIn();
if (loggedIn) {// 验证token有效性/const isValid = await unifiedApiService.getCurrentUser();','/g'/;
if (isValid) {';}}
          navigation.navigate('Main' as never);'}
        }
      }
    } catch (error) {}
}
    }
  };
  // 表单验证
const  validateForm = (): boolean => {}
    const newErrors: LoginFormErrors = {;
    // 邮箱验证
if (!formData.email.trim()) {}
}
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {/;}}/g/;
}
    }
    // 密码验证
if (!formData.password) {}
}
    } else if (formData.password.length < 6) {}
}
    }
    setErrors(newErrors);
return Object.keys(newErrors).length === 0;
  };
  // 处理登录
const  handleLogin = async () => {if (!validateForm()) {}
      return}
    }
    setLoading(true);
setErrors({});
try {// 调用认证服务登录/const  loginResponse = await unifiedApiService.login({)        email: formData.email,)password: formData.password,);/g/;
}
        const rememberMe = formData.rememberMe)}
      ;});
      // 获取用户信息
const userInfo = await unifiedApiService.getCurrentUser();
Alert.alert([;));]          {)';})
}
            onPress: () => navigation.navigate('Main' as never)'}
          }
];
        ];
      );
    } catch (error: any) {setErrors({ ) })}
      ;});
    } finally {}
      setLoading(false)}
    }
  };
  // 处理忘记密码'/,'/g'/;
const  handleForgotPassword = useCallback(() => {';}}
    navigation.navigate('ForgotPassword' as never);'}
  };
  // 处理注册'/,'/g'/;
const  handleRegister = useCallback(() => {';}}
    navigation.navigate('Register' as never);'}
  };
  // 处理第三方登录
const  handleSocialLogin = async (provider: string) => {}
}
  ;};
return (<SafeAreaView style={styles.container}>;)      <KeyboardAvoidingView;'  />/,'/g'/;
style={styles.keyboardContainer}
behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >;
        <ScrollView contentContainerStyle={styles.scrollContainer}>;
          <View style={styles.header}>;
            <Text style={styles.title}>索克生活</Text>
            <Text style={styles.subtitle}>智能健康管理平台</Text>
          </View>
          <View style={styles.form}>;
            {// 邮箱输入}
            <View style={styles.inputContainer}>;
              <Text style={styles.label}>邮箱</Text>
              <TextInput;  />
style={[styles.input, errors.email && styles.inputError]});
);
value={formData.email});
onChangeText={(text) =>}
                  setFormData({  ...formData, email: text ; })
                }
keyboardType="email-address
autoCapitalize="none";
autoCorrect={false}
                editable={!loading}
              />
              {errors.email && (<Text style={styles.errorText}>{errors.email}</Text>)
              )}
            </View>
            {// 密码输入}
            <View style={styles.inputContainer}>;
              <Text style={styles.label}>密码</Text>
              <View style={styles.passwordContainer}>;
                <TextInput;  />
style={[]styles.passwordInput,}
                    errors.password && styles.inputError}
];
                  ]}
                  value={formData.password}
                  onChangeText={(text) =>}
                    setFormData({  ...formData, password: text ; });
                  }","
secureTextEntry={!showPassword}","
autoCapitalize="none";
autoCorrect={false}
                  editable={!loading}
                />
                <TouchableOpacity;  />
style={styles.eyeButton}
                  onPress={() => setShowPassword(!showPassword)}
                >;
                  <Text style={styles.eyeText}>;
                  </Text>
                </TouchableOpacity>
              </View>
              {errors.password && (<Text style={styles.errorText}>{errors.password}</Text>)
              )}
            </View>
            {// 记住我}
            <View style={styles.rememberContainer}>;
              <TouchableOpacity;  />
style={styles.checkbox}
                onPress={() =>setFormData({}                    ...formData,);
}
                    const rememberMe = !formData.rememberMe)}
                  ;});
                }
              >;
                <View;  />
style={[]styles.checkboxInner,}
                    formData.rememberMe && styles.checkboxChecked}
];
                  ]}
                >;
                  {formData.rememberMe && (<Text style={styles.checkmark}>✓</Text>)
                  )}
                </View>
              </TouchableOpacity>
              <Text style={styles.rememberText}>记住我</Text>
            </View>
            {// 通用错误信息}
            {errors.general && (<Text style={styles.generalError}>{errors.general}</Text>)
            )}
            {// 登录按钮}
            <TouchableOpacity;  />
style={[]styles.loginButton,}
                loading && styles.loginButtonDisabled}
];
              ]}
              onPress={handleLogin}
              disabled={loading}
            >
              {loading ? (<ActivityIndicator color="#FFFFFF"  />")"}
              ) : (<Text style={styles.loginButtonText}>登录</Text>)
              )}
            </TouchableOpacity>
            {// 忘记密码}
            <TouchableOpacity;  />
style={styles.forgotPasswordButton}
              onPress={handleForgotPassword}
            >;
              <Text style={styles.forgotPasswordText}>忘记密码？</Text>
            </TouchableOpacity>
            {// 分割线}
            <View style={styles.divider}>;
              <View style={styles.dividerLine}  />
              <Text style={styles.dividerText}>或</Text>
              <View style={styles.dividerLine}  />
            </View>
            {// 第三方登录}
            <View style={styles.socialContainer}>;
              <TouchableOpacity;  />
style={styles.socialButton}
              >;
                <Text style={styles.socialButtonText}>微信登录</Text>
              </TouchableOpacity>
              <TouchableOpacity;  />
style={styles.socialButton}
              >;
                <Text style={styles.socialButtonText}>支付宝登录</Text>
              </TouchableOpacity>
            </View>
            {// 注册链接}
            <View style={styles.registerContainer}>;
              <Text style={styles.registerText}>还没有账号？</Text>
              <TouchableOpacity onPress={handleRegister}>;
                <Text style={styles.registerLink}>立即注册</Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};
const  styles = StyleSheet.create({)container: {,"flex: 1,";
}
    const backgroundColor = '#F5F7FA'}
  }
keyboardContainer: {,}
  const flex = 1}
  }
scrollContainer: {,'flexGrow: 1,'
justifyContent: 'center,'
}
    const paddingHorizontal = 20}
  ;},'
header: {,'alignItems: 'center,'
}
    const marginBottom = 40}
  }
title: {,'fontSize: 32,'
fontWeight: 'bold,'
color: '#2C3E50,'
}
    const marginBottom = 8}
  }
subtitle: {,'fontSize: 16,
}
    const color = '#7F8C8D'}
  ;},'
form: {,'backgroundColor: '#FFFFFF,'';
borderRadius: 16,
padding: 24,
}
    shadowColor: '#000,}'';
shadowOffset: { width: 0, height: 2 }
shadowOpacity: 0.1,
shadowRadius: 8,
const elevation = 5;
  }
inputContainer: {,}
  const marginBottom = 20}
  }
label: {,'fontSize: 16,'
fontWeight: '600,'
color: '#2C3E50,'
}
    const marginBottom = 8}
  }
input: {,'borderWidth: 1,'
borderColor: '#E1E8ED,'';
borderRadius: 8,
paddingHorizontal: 16,
paddingVertical: 12,
fontSize: 16,
}
    const backgroundColor = '#F8F9FA'}
  ;},'
inputError: {,';}}
  const borderColor = '#E74C3C'}
  ;},'
passwordContainer: {,'flexDirection: 'row,'
alignItems: 'center,'';
borderWidth: 1,'
borderColor: '#E1E8ED,'';
borderRadius: 8,
}
    const backgroundColor = '#F8F9FA'}
  }
passwordInput: {flex: 1,
paddingHorizontal: 16,
paddingVertical: 12,
}
    const fontSize = 16}
  }
eyeButton: {paddingHorizontal: 16,
}
    const paddingVertical = 12}
  ;},'
eyeText: {,'color: '#3498DB,'';
fontSize: 14,
}
    const fontWeight = '600'}
  ;},'
errorText: {,'color: '#E74C3C,'';
fontSize: 14,
}
    const marginTop = 4}
  ;},'
rememberContainer: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const marginBottom = 20}
  }
checkbox: {,}
  const marginRight = 8}
  }
checkboxInner: {width: 20,
height: 20,
borderWidth: 2,'
borderColor: '#BDC3C7,'';
borderRadius: 4,'
justifyContent: 'center,'
}
    const alignItems = 'center'}
  ;},'
checkboxChecked: {,'backgroundColor: '#3498DB,'
}
    const borderColor = '#3498DB'}
  ;},'
checkmark: {,'color: '#FFFFFF,'';
fontSize: 12,
}
    const fontWeight = 'bold'}
  }
rememberText: {,'fontSize: 14,
}
    const color = '#7F8C8D'}
  ;},'
generalError: {,'color: '#E74C3C,'';
fontSize: 14,'
textAlign: 'center,'
}
    const marginBottom = 16}
  ;},'
loginButton: {,'backgroundColor: '#3498DB,'';
borderRadius: 8,
paddingVertical: 16,'
alignItems: 'center,'
}
    const marginBottom = 16}
  ;},'
loginButtonDisabled: {,';}}
  const backgroundColor = '#BDC3C7'}
  ;},'
loginButtonText: {,'color: '#FFFFFF,'';
fontSize: 16,
}
    const fontWeight = 'bold'}
  ;},'
forgotPasswordButton: {,'alignItems: 'center,'
}
    const marginBottom = 24}
  ;},'
forgotPasswordText: {,'color: '#3498DB,'';
fontSize: 14,
}
    const fontWeight = '600'}
  ;},'
divider: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const marginBottom = 24}
  }
dividerLine: {flex: 1,
height: 1,
}
    const backgroundColor = '#E1E8ED'}
  }
dividerText: {,'marginHorizontal: 16,'
color: '#7F8C8D,'
}
    const fontSize = 14}
  ;},'
socialContainer: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
}
    const marginBottom = 24}
  }
socialButton: {,'flex: 1,'
backgroundColor: '#F8F9FA,'';
borderRadius: 8,
paddingVertical: 12,'
alignItems: 'center,'';
marginHorizontal: 4,
borderWidth: 1,
}
    const borderColor = '#E1E8ED'}
  ;},'
socialButtonText: {,'color: '#2C3E50,'';
fontSize: 14,
}
    const fontWeight = '600'}
  ;},'
registerContainer: {,'flexDirection: 'row,'
justifyContent: 'center,'
}
    const alignItems = 'center'}
  ;},'
registerText: {,'color: '#7F8C8D,'
}
    const fontSize = 14}
  ;},'
registerLink: {,'color: '#3498DB,'';
fontSize: 14,'
fontWeight: '600,')'
}
    const marginLeft = 4)}
  ;});
});
export default LoginScreen;
''