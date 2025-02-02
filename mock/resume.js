const Mock = require('mockjs')

const List = []
const count = 100

const skillPool = [
  'Java', 'Spring Boot', 'Spring Cloud', 'MyBatis', 'MySQL',
  'JavaScript', 'Vue.js', 'React', 'Angular', 'Node.js',
  'Python', 'Django', 'Flask', 'Pandas', 'TensorFlow',
  'Go', 'Docker', 'Kubernetes', 'Redis', 'MongoDB',
  'HTML5', 'CSS3', 'Webpack', 'Git', 'Linux',
  'AWS', 'Azure', 'Microservices', 'RESTful API', 'GraphQL'
]

const companyPool = [
  '阿里巴巴', '腾讯', '百度', '京东', '字节跳动',
  '美团', '滴滴', '小米', '华为', '网易',
  '携程', '蚂蚁金服', '拼多多', '快手', '新浪',
  '搜狐', '爱奇艺', '哔哩哔哩', '网易有道', '360'
]

const schoolPool = [
  '清华大学', '北京大学', '浙江大学', '复旦大学', '上海交通大学',
  '南京大学', '武汉大学', '中山大学', '华中科技大学', '同济大学',
  '四川大学', '西安交通大学', '哈尔滨工业大学', '东南大学', '中国人民大学'
]

const majorPool = [
  '计算机科学与技术', '软件工程', '信息安全', '人工智能',
  '数据科学与大数据技术', '网络工程', '物联网工程',
  '电子信息工程', '通信工程', '自动化',
  '机械工程', '电气工程', '工商管理', '金融学', '市场营销'
]

const projectPool = [
  {
    name: '企业级微服务平台',
    description: '基于Spring Cloud的微服务架构平台，包含服务注册、配置中心、网关等组件',
    responsibilities: ['架构设计', '核心功能开发', '性能优化', '团队管理']
  },
  {
    name: '电商管理系统',
    description: '基于Vue + Element UI的后台管理系统，实现商品、订单、用户等管理功能',
    responsibilities: ['前端架构', '组件开发', '性能优化', '文档编写']
  },
  {
    name: '数据分析平台',
    description: '使用Python + Pandas进行数据处理和分析，通过可视化展示业务数据',
    responsibilities: ['数据处理', '算法实现', '可视化开发', '需求分析']
  },
  {
    name: '移动端APP',
    description: '使用React Native开发的跨平台移动应用，支持Android和iOS',
    responsibilities: ['UI设计', '功能开发', '性能优化', '跨平台适配']
  }
]

// 修改学历选项映射
const educationMap = {
  'college': '大专',
  'bachelor': '本科',
  'master': '硕士',
  'doctor': '博士'
}

for (let i = 0; i < count; i++) {
  // 生成3-6个随机技能
  const skillCount = Mock.Random.integer(3, 6)
  const skills = Mock.Random.shuffle(skillPool).slice(0, skillCount)

  // 生成2-4段工作经历
  const workCount = Mock.Random.integer(2, 4)
  const workExperience = []
  let currentYear = 2024
  for (let j = 0; j < workCount; j++) {
    const duration = Mock.Random.integer(1, 3)
    const startYear = currentYear - duration
    workExperience.push({
      period: `${startYear}-${currentYear}`,
      company: Mock.Random.pick(companyPool) + Mock.Random.pick(['科技有限公司', '网络有限公司', '信息技术有限公司']),
      position: Mock.Random.pick([
        '高级软件工程师', '前端开发工程师', '后端开发工程师', '全栈工程师',
        '技术主管', '项目经理', '架构师', 'DevOps工程师'
      ]),
      description: Mock.Random.cparagraph(1, 2),
      achievements: Mock.Random.shuffle([
        '优化系统性能提升50%',
        '重构核心模块减少80%代码量',
        '主导团队完成重点项目',
        '获得年度优秀员工',
        '申请多项技术专利'
      ]).slice(0, 2)
    })
    currentYear = startYear
  }

  // 生成1-2段教育经历
  const eduCount = Mock.Random.integer(1, 2)
  const education = []
  currentYear = currentYear - 1
  
  // 先决定最高学历
  const highestDegree = Mock.Random.pick(['college', 'bachelor', 'master', 'doctor'])
  
  for (let j = 0; j < eduCount; j++) {
    const duration = j === 0 ? (highestDegree === 'doctor' ? 3 : highestDegree === 'master' ? 3 : 4) : 4
    const startYear = currentYear - duration
    education.push({
      period: `${startYear}-${currentYear}`,
      school: Mock.Random.pick(schoolPool),
      major: Mock.Random.pick(majorPool),
      degree: j === 0 ? educationMap[highestDegree] : '本科',
      description: Mock.Random.cparagraph(1, 2),
      achievements: [
        Mock.Random.pick([
          '学习成绩优异，多次获得奖学金',
          '担任班级干部，组织多次活动',
          '参与科研项目并发表论文',
          '获得优秀毕业生称号',
          '多次参加编程竞赛获奖'
        ]),
        Mock.Random.pick([
          '获得校级优秀学生称号',
          '参与创新创业项目',
          '获得专业技能证书',
          '参与开源项目贡献',
          '担任学生社团负责人'
        ])
      ]
    })
    currentYear = startYear
  }

  // 生成2-3个项目经历
  const projectCount = Mock.Random.integer(2, 3)
  const projects = Mock.Random.shuffle(projectPool)
    .slice(0, projectCount)
    .map(project => ({
      ...project,
      period: `${Mock.Random.integer(2020, 2023)}-${Mock.Random.integer(2023, 2024)}`,
      responsibility: Mock.Random.shuffle(project.responsibilities).slice(0, 2).join('、')
    }))

  List.push(Mock.mock({
    id: '@increment',
    fileName: '@cname()的简历.@pick(["pdf", "doc", "docx"])',
    uploadTime: '@datetime("yyyy-MM-dd HH:mm:ss")',
    parseStatus: '@pick(["success", "parsing", "failed", "pending"])',
    name: '@cname',
    gender: '@pick(["男", "女"])',
    age: '@integer(22, 45)',
    phone: '1@integer(3000000000, 9999999999)',
    email: '@email',
    education: educationMap[highestDegree], // 直接使用映射值
    educationDetail: education, // 将详细的教育经历存储在单独的字段中
    skills,
    workExperience,
    projects,
    expectedSalary: '@integer(15, 50)k-@integer(51, 80)k',
    currentStatus: '@pick(["在职考虑机会", "在职暂不考虑", "离职寻找机会", "应届生"])',
    source: '@pick(["内部推荐", "猎头推荐", "招聘网站", "校园招聘"])',
    location: '@city',
    selfEvaluation: '@cparagraph(1, 2)',
    updateTime: '@date("yyyy-MM-dd")',
    starred: '@boolean',
    experience: function() {
      const years = this.workExperience.reduce((total, work) => {
        const [start, end] = work.period.split('-')
        return total + (parseInt(end) - parseInt(start))
      }, 0)
      if (years === 0) return '应届生'
      if (years <= 3) return '1-3年'
      if (years <= 5) return '3-5年'
      if (years <= 10) return '5-10年'
      return '10年以上'
    }
  }))
}

module.exports = [
  // 获取解析列表
  {
    url: '/resume/parse/list',
    type: 'get',
    response: config => {
      const { page = 1, limit = 10, keyword, status } = config.query

      let filteredList = [...List]
      
      // 关键词搜索
      if (keyword) {
        const key = keyword.toLowerCase()
        filteredList = filteredList.filter(item => 
          item.name.toLowerCase().includes(key) ||
          item.fileName.toLowerCase().includes(key) ||
          item.skills.some(skill => skill.toLowerCase().includes(key))
        )
      }

      // 状态筛选
      if (status) {
        filteredList = filteredList.filter(item => item.parseStatus === status)
      }

      // 分页
      const start = (page - 1) * limit
      const end = page * limit
      const pageList = filteredList.slice(start, end)

      return {
        code: 20000,
        data: {
          total: filteredList.length,
          items: pageList
        }
      }
    }
  },

  // 解析简历
  {
    url: '/resume/parse/\\d+',
    type: 'post',
    response: {
      code: 20000,
      data: 'success'
    }
  },

  // 获取解析结果
  {
    url: '/resume/parse/result/\\d+',
    type: 'get',
    response: config => {
      const id = parseInt(config.url.match(/\/(\d+)$/)[1])
      const item = List.find(item => item.id === id)

      return {
        code: 20000,
        data: item || {
          error: 'Resume not found'
        }
      }
    }
  },

  // 删除解析记录
  {
    url: '/resume/parse/\\d+',
    type: 'delete',
    response: {
      code: 20000,
      data: 'success'
    }
  },

  // 搜索简历
  {
    url: '/resume/search',
    type: 'get',
    response: config => {
      const { page = 1, limit = 10, keyword, experience, education, skills, startDate, endDate, source, sort } = config.query

      let filteredList = [...List]
      
      // 关键词搜索
      if (keyword) {
        const key = keyword.toLowerCase()
        filteredList = filteredList.filter(item => 
          item.name.toLowerCase().includes(key) ||
          item.skills.some(skill => skill.toLowerCase().includes(key)) ||
          item.workExperience.some(work => 
            work.company.toLowerCase().includes(key) ||
            work.position.toLowerCase().includes(key)
          )
        )
      }

      // 工作经验筛选
      if (experience) {
        filteredList = filteredList.filter(item => {
          const years = item.workExperience.reduce((total, work) => {
            const [start, end] = work.period.split('-')
            return total + (parseInt(end) - parseInt(start))
          }, 0)
          
          switch (experience) {
            case '0': return years === 0
            case '1-3': return years >= 1 && years <= 3
            case '3-5': return years > 3 && years <= 5
            case '5-10': return years > 5 && years <= 10
            case '10+': return years > 10
            default: return true
          }
        })
      }

      // 学历筛选
      if (education) {
        filteredList = filteredList.filter(item => {
          // 直接比较中文值
          return item.education === educationMap[education]
        })
      }

      // 技能筛选
      if (skills && skills.length > 0) {
        const requiredSkills = Array.isArray(skills) ? skills : [skills]
        filteredList = filteredList.filter(item =>
          requiredSkills.every(skill =>
            item.skills.some(s => s.toLowerCase().includes(skill.toLowerCase()))
          )
        )
      }

      // 更新时间范围筛选
      if (startDate && endDate) {
        const start = new Date(startDate).getTime()
        const end = new Date(endDate).getTime()
        filteredList = filteredList.filter(item => {
          const updateTime = new Date(item.updateTime).getTime()
          return updateTime >= start && updateTime <= end
        })
      }

      // 简历来源筛选
      if (source) {
        filteredList = filteredList.filter(item => item.source === source)
      }

      // 排序
      if (sort) {
        switch (sort) {
          case 'updateTime':
            filteredList.sort((a, b) => new Date(b.updateTime) - new Date(a.updateTime))
            break
          case 'experience':
            filteredList.sort((a, b) => b.workExperience.length - a.workExperience.length)
            break
          case 'relevance':
            // 根据关键词匹配度排序
            if (keyword) {
              const key = keyword.toLowerCase()
              filteredList.sort((a, b) => {
                const scoreA = calculateRelevanceScore(a, key)
                const scoreB = calculateRelevanceScore(b, key)
                return scoreB - scoreA
              })
            }
            break
        }
      }

      // 分页
      const start = (page - 1) * limit
      const end = page * limit
      const pageList = filteredList.slice(start, end)

      return {
        code: 20000,
        data: {
          total: filteredList.length,
          items: pageList
        }
      }
    }
  },

  // 下载简历
  {
    url: '/resume/download/\\d+',
    type: 'get',
    response: {
      code: 20000,
      data: 'file content'
    }
  },

  // 收藏/取消收藏
  {
    url: '/resume/star/\\d+',
    type: 'put',
    response: {
      code: 20000,
      data: 'success'
    }
  },

  // 导出搜索结果
  {
    url: '/resume/export',
    type: 'get',
    response: {
      code: 20000,
      data: 'export file content'
    }
  }
]

// 辅助函数：计算相关度分数
function calculateRelevanceScore(item, keyword) {
  let score = 0
  
  // 姓名匹配
  if (item.name.toLowerCase().includes(keyword)) score += 5
  
  // 技能匹配
  score += item.skills.filter(skill => 
    skill.toLowerCase().includes(keyword)
  ).length * 3
  
  // 公司匹配
  score += item.workExperience.filter(work => 
    work.company.toLowerCase().includes(keyword)
  ).length * 2
  
  // 职位匹配
  score += item.workExperience.filter(work => 
    work.position.toLowerCase().includes(keyword)
  ).length * 2
  
  return score
} 