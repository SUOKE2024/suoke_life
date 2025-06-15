// SuokeBench前端应用程序

// 全局变量
let benchmarks = [];
let results = [];
let models = [];
let activeBenchmarkId = null;

// 主函数
document.addEventListener('DOMContentLoaded', () => {
  // 初始化导航
  initNavigation();

  // 加载数据
  fetchDashboardStats();
  fetchBenchmarks();
  fetchRecentRuns();
  fetchResultsList();
  fetchReportsList();

  // 初始化表单
  initBenchmarkForm();
  initSettingsForm();

  // 初始化图表
  initCharts();
});

// 初始化导航
function initNavigation() {
  const navLinks = document.querySelectorAll('nav a');
  const sections = document.querySelectorAll('main section');

  navLinks.forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();

      // 移除所有active类
      navLinks.forEach((l) => l.classList.remove('active'));
      sections.forEach((s) => s.classList.remove('active-section'));

      // 添加active类到当前链接
      link.classList.add('active');

      // 显示对应部分
      const targetId = link.getAttribute('href').substring(1);
      document.getElementById(targetId).classList.add('active-section');
    });
  });
}

// 获取仪表盘统计数据
async function fetchDashboardStats() {
  try {
    const response = await fetch('/api/stats');
    if (!response.ok) {
      throw new Error('获取统计数据失败');
    }

    const data = await response.json();

    // 更新统计卡片
    document.getElementById('completed-benchmarks').textContent =
      data.completed_benchmarks || 0;
    document.getElementById('running-benchmarks').textContent =
      data.running_benchmarks || 0;
    document.getElementById('available-models').textContent =
      data.available_models || 0;
    document.getElementById('data-sets').textContent = data.data_sets || 0;
  } catch (error) {
    console.error('加载统计数据出错:', error);
  }
}

// 获取评测列表
async function fetchBenchmarks() {
  try {
    const response = await fetch('/api/benchmarks');
    if (!response.ok) {
      throw new Error('获取评测列表失败');
    }

    benchmarks = await response.json();

    // 更新评测选择器
    const benchmarkSelect = document.getElementById('benchmark-select');
    benchmarkSelect.innerHTML = '<option value="">-- 选择评测 --</option>';

    benchmarks.forEach((benchmark) => {
      const option = document.createElement('option');
      option.value = benchmark.id;
      option.textContent = benchmark.name;
      benchmarkSelect.appendChild(option);
    });

    // 更新评测卡片
    renderBenchmarkCards(benchmarks);

    // 获取模型列表
    fetchModels();
  } catch (error) {
    console.error('加载评测列表出错:', error);
  }
}

// 获取模型列表
async function fetchModels() {
  try {
    const response = await fetch('/api/models');
    if (!response.ok) {
      throw new Error('获取模型列表失败');
    }

    models = await response.json();

    // 更新模型选择器
    const modelSelect = document.getElementById('model-select');
    modelSelect.innerHTML = '<option value="">-- 选择模型 --</option>';

    models.forEach((model) => {
      const option = document.createElement('option');
      option.value = model.id;
      option.textContent = model.name;
      modelSelect.appendChild(option);
    });
  } catch (error) {
    console.error('加载模型列表出错:', error);
  }
}

// 获取最近运行记录
async function fetchRecentRuns() {
  try {
    const response = await fetch('/api/recent-runs');
    if (!response.ok) {
      throw new Error('获取最近运行记录失败');
    }

    const data = await response.json();

    // 更新最近运行表格
    const tbody = document.getElementById('recent-runs-body');
    tbody.innerHTML = '';

    if (data.length === 0) {
      const tr = document.createElement('tr');
      tr.innerHTML = '<td colspan="6">暂无数据</td>';
      tbody.appendChild(tr);
      return;
    }

    data.forEach((run) => {
      const tr = document.createElement('tr');

      tr.innerHTML = `
                <td>${run.run_id.substring(0, 8)}...</td>
                <td>${run.benchmark_name}</td>
                <td>${run.model_id} (${run.model_version})</td>
                <td><span class="status ${run.status.toLowerCase()}">${getStatusText(
        run.status
      )}</span></td>
                <td>${formatDate(run.created_at)}</td>
                <td>
                    <button class="btn btn-small primary" onclick="viewResult('${
                      run.run_id
                    }')">查看</button>
                </td>
            `;

      tbody.appendChild(tr);
    });
  } catch (error) {
    console.error('加载最近运行记录出错:', error);
  }
}

// 获取结果列表
async function fetchResultsList(page = 1, filter = 'all') {
  try {
    const response = await fetch(`/api/results?page=${page}&status=${filter}`);
    if (!response.ok) {
      throw new Error('获取结果列表失败');
    }

    const data = await response.json();
    results = data.results;

    // 更新结果表格
    const tbody = document.getElementById('results-body');
    tbody.innerHTML = '';

    if (results.length === 0) {
      const tr = document.createElement('tr');
      tr.innerHTML = '<td colspan="8">暂无数据</td>';
      tbody.appendChild(tr);
      return;
    }

    results.forEach((result) => {
      const tr = document.createElement('tr');

      tr.innerHTML = `
                <td>${result.run_id.substring(0, 8)}...</td>
                <td>${result.benchmark_name}</td>
                <td>${result.model_id}</td>
                <td>${result.model_version}</td>
                <td><span class="status ${result.status.toLowerCase()}">${getStatusText(
        result.status
      )}</span></td>
                <td>${formatDate(result.created_at)}</td>
                <td>${
                  result.completed_at ? formatDate(result.completed_at) : '-'
                }</td>
                <td>
                    <button class="btn btn-small primary" onclick="viewResult('${
                      result.run_id
                    }')">详情</button>
                    <button class="btn btn-small" onclick="generateReport('${
                      result.run_id
                    }')">报告</button>
                </td>
            `;

      tbody.appendChild(tr);
    });

    // 更新分页
    renderPagination(data.total, data.page, data.total_pages);
  } catch (error) {
    console.error('加载结果列表出错:', error);
  }
}

// 获取报告列表
async function fetchReportsList() {
  try {
    const response = await fetch('/api/reports');
    if (!response.ok) {
      throw new Error('获取报告列表失败');
    }

    const data = await response.json();

    // 更新报告列表
    const reportList = document.getElementById('report-list');
    reportList.innerHTML = '';

    if (data.length === 0) {
      reportList.innerHTML = '<div class="report-list-item">暂无报告</div>';
      return;
    }

    data.forEach((report) => {
      const div = document.createElement('div');
      div.className = 'report-list-item';
      div.dataset.reportId = report.report_id;
      div.dataset.reportUrl = report.report_url;

      div.innerHTML = `
                <h4>${report.benchmark_name}</h4>
                <p>${report.model_id} (${report.model_version})</p>
                <small>${formatDate(report.created_at)}</small>
            `;

      div.addEventListener('click', () => viewReport(report.report_url));

      reportList.appendChild(div);
    });
  } catch (error) {
    console.error('加载报告列表出错:', error);
  }
}

// 初始化评测表单
function initBenchmarkForm() {
  const form = document.getElementById('benchmark-form');
  const benchmarkSelect = document.getElementById('benchmark-select');
  const parametersContainer = document.getElementById('parameters-container');

  benchmarkSelect.addEventListener('change', () => {
    const benchmarkId = benchmarkSelect.value;
    activeBenchmarkId = benchmarkId;

    // 清空参数容器
    parametersContainer.innerHTML = '';

    if (!benchmarkId) {
      return;
    }

    // 找到选中的评测
    const benchmark = benchmarks.find((b) => b.id === benchmarkId);
    if (!benchmark || !benchmark.parameters) {
      return;
    }

    // 添加参数字段
    Object.entries(benchmark.parameters).forEach(([key, param]) => {
      const formGroup = document.createElement('div');
      formGroup.className = 'form-group';

      const label = document.createElement('label');
      label.setAttribute('for', `param-${key}`);
      label.textContent = param.description || key;

      const input = document.createElement('input');
      input.type = 'text';
      input.id = `param-${key}`;
      input.name = key;
      input.value = param.default || '';

      formGroup.appendChild(label);
      formGroup.appendChild(input);
      parametersContainer.appendChild(formGroup);
    });
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const benchmarkId = benchmarkSelect.value;
    const modelId = document.getElementById('model-select').value;
    const modelVersion = document.getElementById('model-version').value;

    if (!benchmarkId || !modelId || !modelVersion) {
      alert('请填写必填字段');
      return;
    }

    // 收集参数
    const parameters = {};
    const paramInputs = parametersContainer.querySelectorAll('input');
    paramInputs.forEach((input) => {
      parameters[input.name] = input.value;
    });

    // 提交表单
    try {
      const response = await fetch('/api/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          benchmark_id: benchmarkId,
          model_id: modelId,
          model_version: modelVersion,
          parameters: parameters,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || '启动评测失败');
      }

      const result = await response.json();
      alert(`评测已启动！运行ID：${result.run_id}`);

      // 重新加载最近运行记录
      fetchRecentRuns();

      // 切换到结果标签页
      document.querySelector('nav a[href="#results"]').click();
    } catch (error) {
      alert(`错误：${error.message}`);
    }
  });
}

// 初始化设置表单
function initSettingsForm() {
  const form = document.getElementById('settings-form');

  // 加载当前设置
  fetch('/api/settings')
    .then((response) => response.json())
    .then((data) => {
      document.getElementById('data-dir').value = data.data_dir || '';
      document.getElementById('report-dir').value = data.report_dir || '';
      document.getElementById('parallel-runs').value = data.parallel_runs || 4;
      document.getElementById('log-level').value = data.log_level || 'info';
    })
    .catch((error) => console.error('加载设置出错:', error));

  // 表单提交
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const settings = {
      data_dir: document.getElementById('data-dir').value,
      report_dir: document.getElementById('report-dir').value,
      parallel_runs: parseInt(document.getElementById('parallel-runs').value),
      log_level: document.getElementById('log-level').value,
    };

    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || '保存设置失败');
      }

      alert('设置已保存');
    } catch (error) {
      alert(`错误：${error.message}`);
    }
  });
}

// 初始化图表
function initCharts() {
  // 智能体性能对比图
  fetch('/api/agent-performance')
    .then((response) => response.json())
    .then((data) => {
      const ctx = document.getElementById('agentChart').getContext('2d');

      new Chart(ctx, {
        type: 'radar',
        data: {
          labels: data.metrics,
          datasets: data.agents.map((agent) => ({
            label: agent.name,
            data: agent.scores,
            borderColor: agent.color,
            backgroundColor: `${agent.color}33`,
            borderWidth: 2,
          })),
        },
        options: {
          scales: {
            r: {
              beginAtZero: true,
              max: 100,
            },
          },
        },
      });
    })
    .catch((error) => console.error('加载智能体性能数据出错:', error));

  // 评测类型分布图
  fetch('/api/task-distribution')
    .then((response) => response.json())
    .then((data) => {
      const ctx = document.getElementById('taskChart').getContext('2d');

      new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: data.map((item) => item.task),
          datasets: [
            {
              data: data.map((item) => item.count),
              backgroundColor: [
                '#1e88e5',
                '#26a69a',
                '#ff5722',
                '#9c27b0',
                '#673ab7',
                '#3f51b5',
                '#2196f3',
                '#03a9f4',
              ],
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'right',
            },
          },
        },
      });
    })
    .catch((error) => console.error('加载任务分布数据出错:', error));
}

// 渲染评测卡片
function renderBenchmarkCards(benchmarks) {
  const container = document.getElementById('benchmarks-grid');
  container.innerHTML = '';

  benchmarks.forEach((benchmark) => {
    const card = document.createElement('div');
    card.className = 'benchmark-card';

    card.innerHTML = `
            <h4>${benchmark.name}</h4>
            <p>${benchmark.description}</p>
            <div class="benchmark-tags">
                <span class="tag">${getTaskName(benchmark.task)}</span>
                ${benchmark.tags
                  .map((tag) => `<span class="tag">${tag}</span>`)
                  .join('')}
            </div>
            <div class="card-footer" style="margin-top: 1rem;">
                <button class="btn primary" onclick="selectBenchmark('${
                  benchmark.id
                }')">选择</button>
            </div>
        `;

    container.appendChild(card);
  });
}

// 渲染分页
function renderPagination(total, currentPage, totalPages) {
  const container = document.getElementById('results-pagination');
  container.innerHTML = '';

  if (totalPages <= 1) {
    return;
  }

  // 上一页按钮
  const prevButton = document.createElement('button');
  prevButton.textContent = '上一页';
  prevButton.disabled = currentPage === 1;
  prevButton.addEventListener('click', () => {
    if (currentPage > 1) {
      const filter = document.getElementById('result-filter').value;
      fetchResultsList(currentPage - 1, filter);
    }
  });
  container.appendChild(prevButton);

  // 页码按钮
  for (let i = 1; i <= totalPages; i++) {
    const pageButton = document.createElement('button');
    pageButton.textContent = i;
    pageButton.classList.toggle('active', i === currentPage);
    pageButton.addEventListener('click', () => {
      const filter = document.getElementById('result-filter').value;
      fetchResultsList(i, filter);
    });
    container.appendChild(pageButton);
  }

  // 下一页按钮
  const nextButton = document.createElement('button');
  nextButton.textContent = '下一页';
  nextButton.disabled = currentPage === totalPages;
  nextButton.addEventListener('click', () => {
    if (currentPage < totalPages) {
      const filter = document.getElementById('result-filter').value;
      fetchResultsList(currentPage + 1, filter);
    }
  });
  container.appendChild(nextButton);
}

// 辅助函数：查看结果
function viewResult(runId) {
  window.location.href = `/api/result-ui?run_id=${runId}`;
}

// 辅助函数：生成报告
async function generateReport(runId) {
  try {
    const response = await fetch('/api/report', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        run_id: runId,
        format: 'HTML',
        include_samples: true,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '生成报告失败');
    }

    const result = await response.json();
    alert("报告生成成功！");

    // 查看报告
    viewReport(result.report_url);

    // 重新加载报告列表
    fetchReportsList();

    // 切换到报告标签页
    document.querySelector('nav a[href="#reports"]').click();
  } catch (error) {
    alert(`错误：${error.message}`);
  }
}

// 辅助函数：查看报告
function viewReport(reportUrl) {
  // 更新报告列表项的活动状态
  const items = document.querySelectorAll('.report-list-item');
  items.forEach((item) => {
    if (item.dataset.reportUrl === reportUrl) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // 加载报告内容
  const reportContent = document.getElementById('report-content');
  reportContent.innerHTML =
    '<div class="report-placeholder"><div class="loading"></div> 加载中...</div>';

  fetch(reportUrl)
    .then((response) => response.text())
    .then((html) => {
      reportContent.innerHTML = html;
    })
    .catch((error) => {
      reportContent.innerHTML = `<div class="report-placeholder">加载报告出错: ${error.message}</div>`;
    });
}

// 辅助函数：选择评测
function selectBenchmark(benchmarkId) {
  document.getElementById('benchmark-select').value = benchmarkId;

  // 触发change事件
  const event = new Event('change');
  document.getElementById('benchmark-select').dispatchEvent(event);

  // 滚动到表单
  document
    .querySelector('.run-benchmark-form')
    .scrollIntoView({ behavior: 'smooth' });
}

// 辅助函数：格式化日期
function formatDate(dateString) {
  if (!dateString) {
    return '-';
  }

  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// 辅助函数：获取状态文本
function getStatusText(status) {
  const statusMap = {
    RUNNING: '运行中',
    COMPLETED: '已完成',
    FAILED: '失败',
    PENDING: '等待中',
  };

  return statusMap[status] || status;
}

// 辅助函数：获取任务名称
function getTaskName(taskType) {
  const taskMap = {
    TCM_DIAGNOSIS: '中医辨证',
    TONGUE_RECOGNITION: '舌象识别',
    FACE_RECOGNITION: '面色识别',
    PULSE_RECOGNITION: '脉象识别',
    HEALTH_PLAN_GENERATION: '健康方案生成',
    AGENT_COLLABORATION: '智能体协作',
    PRIVACY_VERIFICATION: '隐私验证',
    EDGE_PERFORMANCE: '端侧性能',
    DIALECT_RECOGNITION: '方言识别',
  };

  return taskMap[taskType] || taskType;
}
