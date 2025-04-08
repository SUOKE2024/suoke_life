package mocks

// MockHttpClient 模拟HTTP客户端
type MockHttpClient struct {
	// 记录调用历史
	Calls struct {
		Post []struct {
			URL     string
			Body    interface{}
			Headers map[string]string
		}
	}

	// 配置响应
	PostResponse struct {
		Data  []byte
		Error error
	}
}

// Post 实现POST请求接口
func (m *MockHttpClient) Post(url string, body interface{}, headers map[string]string) ([]byte, error) {
	// 记录调用
	m.Calls.Post = append(m.Calls.Post, struct {
		URL     string
		Body    interface{}
		Headers map[string]string
	}{
		URL:     url,
		Body:    body,
		Headers: headers,
	})

	// 返回配置的响应
	return m.PostResponse.Data, m.PostResponse.Error
}
