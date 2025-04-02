import Joi from 'joi';

export const accessibilityProfileSchema = Joi.object({
  visualSettings: Joi.object({
    textSize: Joi.string().valid('small', 'medium', 'large', 'x-large'),
    highContrast: Joi.boolean(),
    reduceMotion: Joi.boolean(),
    colorBlindMode: Joi.string().valid('none', 'protanopia', 'deuteranopia', 'tritanopia', 'achromatopsia'),
    screenReader: Joi.boolean(),
    invertColors: Joi.boolean(),
    fontType: Joi.string().valid('default', 'dyslexic', 'sans-serif', 'serif')
  }),
  
  audioSettings: Joi.object({
    voiceFeedback: Joi.boolean(),
    soundEffects: Joi.boolean(),
    hapticFeedback: Joi.boolean(),
    voiceRecognition: Joi.boolean(),
    voiceSpeed: Joi.number().min(0.5).max(2.0),
    voicePitch: Joi.number().min(0.5).max(2.0)
  }),
  
  interactionSettings: Joi.object({
    autoCompleteEnabled: Joi.boolean(),
    extendedTouch: Joi.boolean(),
    singleTapMode: Joi.boolean(),
    keyboardNavigation: Joi.boolean(),
    gestureControl: Joi.boolean(),
    mouseDwell: Joi.boolean(),
    mouseSpeed: Joi.number().min(0.5).max(2.0)
  }),
  
  navigationSettings: Joi.object({
    simplifiedNavigation: Joi.boolean(),
    shortcutsEnabled: Joi.boolean(),
    breadcrumbsEnabled: Joi.boolean(),
    pageStructure: Joi.string().valid('standard', 'simplified', 'minimal')
  }),
  
  dialectPreference: Joi.string()
}).min(1).messages({
  'object.min': '至少需要提供一项设置进行更新'
}); 