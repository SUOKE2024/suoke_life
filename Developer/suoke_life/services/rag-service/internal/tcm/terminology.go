package tcm

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"sync"

	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

// TCMTerm 中医术语
type TCMTerm struct {
	// Term 术语名称
	Term string `json:"term"`
	
	// Category 术语类别
	Category string `json:"category"`
	
	// Description 术语描述
	Description string `json:"description,omitempty"`
	
	// Synonyms 同义词
	Synonyms []string `json:"synonyms,omitempty"`
	
	// Related 相关术语
	Related []string `json:"related,omitempty"`
	
	// Weight 权重
	Weight float64 `json:"weight,omitempty"`
}

// TerminologyProcessor 中医术语处理器
type TerminologyProcessor struct {
	// 术语库
	terms map[string]*TCMTerm
	
	// 同义词映射
	synonymMap map[string]string
	
	// 日志器
	logger utils.Logger
	
	// 加载锁
	loadLock sync.Mutex
	
	// 是否已初始化
	initialized bool
}

// NewTerminologyProcessor 创建中医术语处理器
func NewTerminologyProcessor(logger utils.Logger) *TerminologyProcessor {
	if logger == nil {
		logger = utils.NewNoopLogger()
	}
	
	return &TerminologyProcessor{
		terms:      make(map[string]*TCMTerm),
		synonymMap: make(map[string]string),
		logger:     logger,
	}
}

// Initialize 初始化术语处理器
func (p *TerminologyProcessor) Initialize(ctx context.Context, termLibraryPath string) error {
	p.loadLock.Lock()
	defer p.loadLock.Unlock()
	
	if p.initialized {
		p.logger.Debug("术语处理器已初始化，跳过")
		return nil
	}
	
	// 从文件加载术语库
	if err := p.loadTerms(termLibraryPath); err != nil {
		return fmt.Errorf("加载术语库失败: %w", err)
	}
	
	// 构建同义词映射
	p.buildSynonymMap()
	
	p.initialized = true
	p.logger.Info("术语处理器初始化完成", "terms_count", len(p.terms), "synonyms_count", len(p.synonymMap))
	
	return nil
}

// EnhanceText 增强文本中的中医术语
func (p *TerminologyProcessor) EnhanceText(text string) string {
	if !p.initialized {
		p.logger.Warn("术语处理器未初始化，返回原始文本")
		return text
	}
	
	// 优先处理较长的术语，防止子串覆盖
	enhancedText := text
	
	// 首先处理直接术语
	for term, info := range p.terms {
		if strings.Contains(enhancedText, term) {
			enhancedText = strings.ReplaceAll(
				enhancedText,
				term,
				fmt.Sprintf("[TCM:%s:%s]%s[/TCM]", info.Category, term, term),
			)
		}
	}
	
	// 然后处理同义词
	for synonym, term := range p.synonymMap {
		if strings.Contains(enhancedText, synonym) {
			info := p.terms[term]
			enhancedText = strings.ReplaceAll(
				enhancedText,
				synonym,
				fmt.Sprintf("[TCM:%s:%s]%s[/TCM]", info.Category, term, synonym),
			)
		}
	}
	
	return enhancedText
}

// GetTermInfo 获取术语信息
func (p *TerminologyProcessor) GetTermInfo(term string) (*TCMTerm, bool) {
	// 检查是否为直接术语
	if info, found := p.terms[term]; found {
		return info, true
	}
	
	// 检查是否为同义词
	if canonicalTerm, found := p.synonymMap[term]; found {
		info, exists := p.terms[canonicalTerm]
		return info, exists
	}
	
	return nil, false
}

// ExtractTerms 从文本中提取中医术语
func (p *TerminologyProcessor) ExtractTerms(text string) []TCMTerm {
	if !p.initialized {
		p.logger.Warn("术语处理器未初始化，无法提取术语")
		return nil
	}
	
	foundTerms := make(map[string]bool)
	var result []TCMTerm
	
	// 提取直接术语
	for term, info := range p.terms {
		if strings.Contains(text, term) && !foundTerms[term] {
			foundTerms[term] = true
			result = append(result, *info)
		}
	}
	
	// 提取同义词
	for synonym, term := range p.synonymMap {
		if strings.Contains(text, synonym) && !foundTerms[term] {
			foundTerms[term] = true
			if info, found := p.terms[term]; found {
				result = append(result, *info)
			}
		}
	}
	
	return result
}

// CalculateTermRelevance 计算文本与中医术语的相关性
func (p *TerminologyProcessor) CalculateTermRelevance(text string) float64 {
	if !p.initialized {
		return 0.0
	}
	
	extractedTerms := p.ExtractTerms(text)
	if len(extractedTerms) == 0 {
		return 0.0
	}
	
	// 简单计算术语数量和权重总和
	termCount := len(extractedTerms)
	weightSum := 0.0
	
	for _, term := range extractedTerms {
		weightSum += term.Weight
	}
	
	// 计算相关性分数
	baseScore := float64(termCount) * 0.05
	weightScore := weightSum * 0.05
	
	return baseScore + weightScore
}

// GetTermsByCategory 按类别获取术语
func (p *TerminologyProcessor) GetTermsByCategory(category string) []TCMTerm {
	var result []TCMTerm
	
	for _, term := range p.terms {
		if term.Category == category {
			result = append(result, *term)
		}
	}
	
	return result
}

// GetAllTerms 获取所有术语
func (p *TerminologyProcessor) GetAllTerms() []TCMTerm {
	result := make([]TCMTerm, 0, len(p.terms))
	
	for _, term := range p.terms {
		result = append(result, *term)
	}
	
	return result
}

// 从文件加载术语库
func (p *TerminologyProcessor) loadTerms(filePath string) error {
	// 打开文件
	file, err := os.Open(filePath)
	if err != nil {
		return fmt.Errorf("打开术语库文件失败: %w", err)
	}
	defer file.Close()
	
	// 解析JSON
	var terms []TCMTerm
	decoder := json.NewDecoder(file)
	if err := decoder.Decode(&terms); err != nil {
		return fmt.Errorf("解析术语库文件失败: %w", err)
	}
	
	// 存储术语
	for i := range terms {
		term := terms[i]
		p.terms[term.Term] = &term
		
		// 设置默认权重
		if term.Weight <= 0 {
			p.terms[term.Term].Weight = 1.0
		}
	}
	
	return nil
}

// 构建同义词映射
func (p *TerminologyProcessor) buildSynonymMap() {
	for term, info := range p.terms {
		for _, synonym := range info.Synonyms {
			p.synonymMap[synonym] = term
		}
	}
}

// 加载默认术语（当术语库文件不存在时使用）
func (p *TerminologyProcessor) loadDefaultTerms() {
	defaultTerms := []TCMTerm{
		{Term: "阴阳", Category: "基础理论", Description: "中医基本理论，描述事物对立统一的两个方面", Weight: 1.2, 
			Synonyms: []string{"阴阳学说", "阴阳理论"}, Related: []string{"五行", "气血"}},
		{Term: "五行", Category: "基础理论", Description: "木火土金水五种基本元素及其相互关系", Weight: 1.2,
			Synonyms: []string{"五行学说", "五行理论"}, Related: []string{"阴阳", "相生相克"}},
		{Term: "气血", Category: "基础理论", Description: "构成人体和维持人体生命活动的基本物质", Weight: 1.1,
			Synonyms: []string{"气血学说"}, Related: []string{"精气神", "阴阳"}},
		{Term: "脏腑", Category: "解剖生理", Description: "中医对人体内脏器官的总称", Weight: 1.0,
			Synonyms: []string{"五脏六腑"}, Related: []string{"经络", "气血"}},
		{Term: "经络", Category: "解剖生理", Description: "运行气血、联系脏腑肢节的通道", Weight: 1.1,
			Synonyms: []string{"经脉", "络脉"}, Related: []string{"穴位", "脏腑"}},
		{Term: "寒热", Category: "病因病机", Description: "疾病的性质和表现", Weight: 0.9,
			Synonyms: []string{"寒症", "热症"}, Related: []string{"虚实", "表里"}},
		{Term: "虚实", Category: "病因病机", Description: "病邪盛衰和正气强弱的关系", Weight: 0.9,
			Synonyms: []string{"虚证", "实证"}, Related: []string{"寒热", "表里"}},
		{Term: "舌诊", Category: "诊断", Description: "通过观察舌象诊断疾病", Weight: 1.0,
			Synonyms: []string{"望舌", "看舌象"}, Related: []string{"脉诊", "面诊"}},
		{Term: "脉诊", Category: "诊断", Description: "通过切脉诊断疾病", Weight: 1.0,
			Synonyms: []string{"切脉", "号脉"}, Related: []string{"舌诊", "面诊"}},
		{Term: "辨证论治", Category: "治疗", Description: "根据证候分析确定治疗方法", Weight: 1.2,
			Synonyms: []string{"辨证施治"}, Related: []string{"望闻问切", "治法"}},
	}
	
	for i := range defaultTerms {
		term := defaultTerms[i]
		p.terms[term.Term] = &term
	}
	
	p.buildSynonymMap()
}

// 从文本文件加载术语库
func (p *TerminologyProcessor) loadTermsFromTextFile(filePath string) error {
	// 打开文件
	file, err := os.Open(filePath)
	if err != nil {
		return fmt.Errorf("打开术语库文件失败: %w", err)
	}
	defer file.Close()
	
	// 逐行读取
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue // 跳过空行和注释行
		}
		
		// 解析行内容（假设格式为"术语|类别|描述|同义词1,同义词2|相关词1,相关词2|权重"）
		parts := strings.Split(line, "|")
		if len(parts) < 2 {
			continue // 至少需要术语和类别
		}
		
		term := TCMTerm{
			Term:     strings.TrimSpace(parts[0]),
			Category: strings.TrimSpace(parts[1]),
			Weight:   1.0, // 默认权重
		}
		
		if len(parts) >= 3 {
			term.Description = strings.TrimSpace(parts[2])
		}
		
		if len(parts) >= 4 && parts[3] != "" {
			term.Synonyms = splitAndTrim(parts[3], ",")
		}
		
		if len(parts) >= 5 && parts[4] != "" {
			term.Related = splitAndTrim(parts[4], ",")
		}
		
		if len(parts) >= 6 {
			fmt.Sscanf(parts[5], "%f", &term.Weight)
		}
		
		p.terms[term.Term] = &term
	}
	
	if err := scanner.Err(); err != nil {
		return fmt.Errorf("读取术语库文件失败: %w", err)
	}
	
	return nil
}

// 辅助函数：分割并去除空格
func splitAndTrim(s string, sep string) []string {
	parts := strings.Split(s, sep)
	result := make([]string, 0, len(parts))
	
	for _, part := range parts {
		trimmed := strings.TrimSpace(part)
		if trimmed != "" {
			result = append(result, trimmed)
		}
	}
	
	return result
} 