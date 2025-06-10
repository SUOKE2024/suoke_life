// 无障碍服务客户端 - 对应后端Python的AccessibilityClient实现/;/g/;

// API响应接口/;,/g/;
interface ApiResponse<T = any> {data: T}const success = boolean;
message?: string;
}
  code?: number;}
}

// 导入类型/;,/g/;
interface AccessibilityNeeds {visualImpairment: boolean}hearingImpairment: boolean,;
motorImpairment: boolean,;
}
}
  const cognitiveSupport = boolean;}
}

interface UserProfile {id: string}name: string,;
}
}
  const accessibilityNeeds = AccessibilityNeeds;}
}

interface ImageData {uri?: string;,}base64?: string;
width?: number;
}
}
  height?: number;}
}

interface AudioData {uri?: string;,}base64?: string;
}
}
  duration?: number;}
}

// 无障碍服务配置/;,/g/;
const  ACCESSIBILITY_API_CONFIG = {baseUrl: 'http://localhost:8000', // 无障碍服务地址'/;}}'/g'/;
  const timeout = 30000;}
};

// 无障碍服务响应类型/;,/g/;
export interface AccessibilityResponse {;,}const success = boolean;
data?: unknown;
}
}
  error?: string;}
}

export interface VoiceAssistanceResponse {recognized_text: string}response_text: string,;
response_audio: string,;
confidence: number,;
const success = boolean;
}
}
  error?: string;}
}

export interface ImageAssistanceResponse {scene_description: string}medical_features: Array<{type: string,;
description: string,;
}
}
    const confidence = number;}
  }>;
navigation_guidance: string,;
confidence: number,;
audio_guidance: string,;
const success = boolean;
error?: string;
}

export interface SignLanguageResponse {recognized_text: string}confidence: number,;
segments: Array<{text: string,;
start_time_ms: number,;
end_time_ms: number,;
}
}
    const confidence = number;}
  }>;
const success = boolean;
error?: string;
}

export interface AccessibleContentResponse {accessible_content: string}content_url: string,;
audio_content: string,;
tactile_content: string; // 盲文内容,/;,/g/;
const success = boolean;
}
}
  error?: string;}
}

export interface ScreenReadingResponse {screen_description: string}ui_elements: Array<{element_type: string,;
content: string,;
action: string,;
location: {x: number,;
y: number,;
width: number,;
}
}
      const height = number;}
    };
  }>;
audio_description: string,;
const success = boolean;
error?: string;
}

export interface AccessibilitySettingsResponse {current_preferences: {language: string,;
voice_type: string,;
speech_rate: number,;
high_contrast: boolean,;
screen_reader: boolean,;
const font_size = string;
}
}
    [key: string]: unknown;}
  };
success: boolean,;
const message = string;
error?: string;
}

// 无障碍服务客户端 - 对应后端Python的AccessibilityClient实现/;,/g/;
export class AccessibilityServiceClient {;,}private baseUrl: string;
private timeout: number;
constructor() {this.baseUrl = ACCESSIBILITY_API_CONFIG.baseUrl;}}
}
    this.timeout = ACCESSIBILITY_API_CONFIG.timeout;}
  }

  // 处理语音输入，支持语音识别和语音辅助/;,/g,/;
  async: processVoiceInput(audioData: AudioData,';,)userId: string,';,'';
context: string = 'diagnosis';',')';,'';
language: string = 'zh-CN';',)'';
dialect: string = 'standard')';'';
  ): Promise<VoiceAssistanceResponse> {try {}      const formData = new FormData();
';,'';
if (audioData.base64) {';}}'';
        formData.append('audio_data', audioData.base64);'}'';'';
      } else if (audioData.uri) {const response = await fetch(audioData.uri);';,}const blob = await response.blob();';'';
}
        formData.append('audio_file', blob);'}'';'';
      }';'';
';,'';
formData.append('user_id', userId);';,'';
formData.append('context', context);';,'';
formData.append('language', language);';,'';
formData.append('dialect', dialect);';,'';
const: response = await fetch(`${this.baseUrl}/api/v1/accessibility/voice-assistance`,``'/`;)        {';,}method: 'POST';','';'/g'/`;
}
          body: formData,')}'';
headers: { Accept: 'application/json' ;},')''/;'/g'/;
        });
      );
if (!response.ok) {}
        const throw = new Error(`HTTP error! status: ${response.status;}`);````;```;
      }

      const result = await response.json();';,'';
return {';,}recognized_text: result.recognized_text || ';',';,'';
response_text: result.response_text || ';',';,'';
response_audio: result.response_audio || ';',';,'';
confidence: result.confidence || 0.0,;
}
        const success = true;}
      };
    } catch (error) {';,}return {';,}recognized_text: ';',';'';
';,'';
response_audio: ';','';
confidence: 0.0,;
success: false,;
}
        const error = (error as Error).message;}
      };
    }
  }

  // 处理图像输入，支持图像识别和描述/;,/g,/;
  async: processImageInput(imageData: ImageData,';,)userId: string,')'';
imageType: string = 'tongue';',')';,'';
context: string = 'looking_diagnosis')';'';
  ): Promise<ImageAssistanceResponse> {try {}      const formData = new FormData();
';,'';
if (imageData.base64) {';}}'';
        formData.append('image_data', imageData.base64);'}'';'';
      } else if (imageData.uri) {const response = await fetch(imageData.uri);';,}const blob = await response.blob();';'';
}
        formData.append('image_file', blob);'}'';'';
      }';'';
';,'';
formData.append('user_id', userId);';,'';
formData.append('image_type', imageType);';,'';
formData.append('context', context);';,'';
formData.append('preferences',';,)JSON.stringify({)';,}language: 'zh-CN';',')';,'';
detail_level: 'high';',)'';'';
}
          const medical_context = true;)}
        });
      );
const: response = await fetch(`${this.baseUrl}/api/v1/accessibility/image-assistance`,``'/`;)        {';,}method: 'POST';','';'/g'/`;
}
          body: formData,')}'';
headers: { Accept: 'application/json' ;},')''/;'/g'/;
        });
      );
if (!response.ok) {}
        const throw = new Error(`HTTP error! status: ${response.status;}`);````;```;
      }

      const result = await response.json();';,'';
return {';,}scene_description: result.scene_description || ';',';,'';
medical_features: result.medical_features || [],';,'';
navigation_guidance: result.navigation_guidance || ';',';,'';
confidence: result.confidence || 0.0,';,'';
audio_guidance: result.audio_guidance || ';',';'';
}
        const success = true;}
      };
    } catch (error) {return {}';,'';
medical_features: [],';,'';
navigation_guidance: ';',';,'';
confidence: 0.0,';,'';
audio_guidance: ';','';
success: false,;
}
        const error = (error as Error).message;}
      };
    }
  }

  // 处理手语输入，支持手语识别/;,/g,/;
  async: processSignLanguageInput(videoData: Blob,)';,'';
userId: string,)';,'';
language: string = 'csl')';'';
  ): Promise<SignLanguageResponse> {try {';,}const formData = new FormData();';,'';
formData.append('video_file', videoData);';,'';
formData.append('user_id', userId);';,'';
formData.append('language', language);';'';
}
}
      const: response = await fetch(`${this.baseUrl}/api/v1/accessibility/sign-language`,``'/`;)        {';,}method: 'POST';','';'/g'/`;
}
          body: formData,')}'';
headers: { Accept: 'application/json' ;},')''/;'/g'/;
        });
      );
if (!response.ok) {}
        const throw = new Error(`HTTP error! status: ${response.status;}`);````;```;
      }

      const result = await response.json();';,'';
return {';,}recognized_text: result.recognized_text || ';',';,'';
confidence: result.confidence || 0.0,;
segments: result.segments || [],;
}
        const success = true;}
      };
    } catch (error) {return {}        confidence: 0.0,;
segments: [],;
success: false,;
}
        const error = (error as Error).message;}
      };
    }
  }

  // 生成无障碍健康内容/;,/g,/;
  async: generateAccessibleHealthContent(content: string,';,)userId: string,')'';
contentType: string = 'diagnosis_result';',')';,'';
targetFormat: string = 'audio')';'';
  ): Promise<AccessibleContentResponse> {}}
    try {}
      response: await fetch(`${this.baseUrl;}/api/v1/accessibility/accessible-content`,``'/`;)        {';,}method: 'POST';','';,'/g'/`;
const headers = {';}            'Content-Type': 'application/json','/;'/g'/;
}
            const Accept = 'application/json';'}''/;'/g'/;
          }
const body = JSON.stringify({)content}user_id: userId,;
content_type: contentType,;
target_format: targetFormat,';,'';
preferences: {,';,}language: 'zh-CN';','';
voice_type: 'female';','';
speech_rate: 1.0,);
}
              const high_contrast = false;)}
            },);
          }),;
        }
      );
if (!response.ok) {}
        const throw = new Error(`HTTP error! status: ${response.status;}`);````;```;
      }

      const result = await response.json();';,'';
return {';,}accessible_content: result.accessible_content || ';',';,'';
content_url: result.content_url || ';',';,'';
audio_content: result.audio_content || ';',';,'';
tactile_content: result.tactile_content || ';','';'';
}
        const success = true;}
      };
    } catch (error) {return {';}';,'';
content_url: ';',';,'';
audio_content: ';',';,'';
tactile_content: ';',';,'';
success: false,;
}
        const error = (error as Error).message;}
      };
    }
  }

  // 屏幕阅读功能/;,/g,/;
  async: performScreenReading(screenData: string,)';,'';
userId: string,)';,'';
readingMode: string = 'full')';'';
  ): Promise<ScreenReadingResponse> {}}
    try {}
      response: await fetch(`${this.baseUrl;}/api/v1/accessibility/screen-reading`,``'/`;)        {';,}method: 'POST';','';,'/g'/`;
const headers = {';}            'Content-Type': 'application/json','/;'/g'/;
}
            const Accept = 'application/json';'}''/;'/g'/;
          }
body: JSON.stringify({)}screen_data: screenData,;
user_id: userId,;
reading_mode: readingMode,';,'';
preferences: {,';,}language: 'zh-CN';','';
voice_type: 'female';',')'';'';
}
              const speech_rate = 1.0;)}
            },);
          }),;
        }
      );
if (!response.ok) {}
        const throw = new Error(`HTTP error! status: ${response.status;}`);````;```;
      }

      const result = await response.json();';,'';
return {';,}screen_description: result.screen_description || ';',';,'';
ui_elements: result.ui_elements || [],';,'';
audio_description: result.audio_description || ';',';'';
}
        const success = true;}
      };
    } catch (error) {return {}';,'';
ui_elements: [],';,'';
audio_description: ';','';
success: false,;
}
        const error = (error as Error).message;}
      };
    }
  }

  // 获取和更新无障碍设置/;,/g/;
const async = getAccessibilitySettings(userId: string);
  ): Promise<AccessibilitySettingsResponse> {}}
    try {}
      response: await fetch(`${this.baseUrl;}/api/v1/accessibility/settings/${userId}`,``'/`;)        {';}}'/g,'/`;
  method: 'GET';',')}';,'';
headers: { Accept: 'application/json' ;},')''/;'/g'/;
        });
      );
if (!response.ok) {}
        const throw = new Error(`HTTP error! status: ${response.status;}`);````;```;
      }

      const result = await response.json();
return {}
        current_preferences: result.current_preferences || {;}
const success = true;

      };
    } catch (error) {return {';,}current_preferences: {,';,}language: 'zh-CN';','';
voice_type: 'female';','';
speech_rate: 1.0,;
high_contrast: false,';,'';
screen_reader: false,';'';
}
          const font_size = 'medium';'}'';'';
        }
success: false,;
const error = (error as Error).message;
      };
    }
  }

  async: updateAccessibilitySettings(userId: string,);
settings: Record<string, unknown>);
  ): Promise<AccessibilitySettingsResponse> {}}
    try {}
      response: await fetch(`${this.baseUrl;}/api/v1/accessibility/settings/${userId}`,``'/`;)        {';,}method: 'PUT';','';,'/g'/`;
const headers = {';}            'Content-Type': 'application/json',')''/;'/g'/;
}
            const Accept = 'application/json';')}''/;'/g'/;
          },);
body: JSON.stringify({ settings ;}),;
        }
      );
if (!response.ok) {}
        const throw = new Error(`HTTP error! status: ${response.status;}`);````;```;
      }

      const result = await response.json();
return {current_preferences: result.current_preferences || settings}const success = true;
}
}
      };
    } catch (error) {return {';,}current_preferences: {,';,}language: 'zh-CN';','';
voice_type: 'female';','';
speech_rate: 1.0,;
high_contrast: false,';,'';
screen_reader: false,';'';
}
          const font_size = 'medium';'}'';'';
        }
success: false,;
const error = (error as Error).message;
      };
    }
  }
}

// 创建无障碍服务客户端实例/;,/g/;
export const accessibilityServiceClient = new AccessibilityServiceClient();
export default AccessibilityServiceClient;';'';
''';