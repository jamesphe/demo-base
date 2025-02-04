const Mock = require('mockjs')
const { param2Obj } = require('./utils')

const List = []
const count = 20

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
  },

  // 获取聊天历史记录
  {
    url: '/api/resume/chat-history',
    type: 'get',
    response: () => {
      return {
        code: 20000,
        data: chatList
      }
    }
  },

  // AI对话接口
  {
    url: '/api/resume/ai-chat',
    type: 'post',
    response: config => {
      const { message } = config.body
      
      // 模拟AI根据关键词匹配简历
      const matchedResumes = resumes.filter(resume => {
        const keywords = message.toLowerCase()
        return resume.skills.some(skill => keywords.includes(skill.toLowerCase())) ||
               resume.title.toLowerCase().includes(keywords) ||
               String(resume.experience).includes(keywords)
      })

      // 根据匹配数量返回不同的回复
      let reply = ''
      if (matchedResumes.length === 0) {
        reply = '抱歉，没有找到完全匹配的简历，您可以尝试调整搜索条件或描述具体的技能要求。'
      } else if (matchedResumes.length === 1) {
        reply = `我找到了1份非常匹配的简历。这位候选人是${matchedResumes[0].name}，${matchedResumes[0].title}，有${matchedResumes[0].experience}年工作经验，教育背景为${matchedResumes[0].education}。`
      } else {
        reply = `我找到了${matchedResumes.length}份相关简历。您可以查看下面的简历卡片，了解每位候选人的具体情况。如果想要进一步筛选，您可以告诉我更具体的要求，比如：\n` +
                '- 期望的工作年限\n' +
                '- 具体的技术栈要求\n' +
                '- 教育背景要求\n' +
                '或者您也可以告诉我最关注哪方面的能力，我可以帮您重点推荐。'
      }

      // 计算每个简历的匹配度分数
      const scoredResumes = matchedResumes.map(resume => {
        const score = calculateMatchScore(resume, message)
        return { ...resume, matchScore: score }
      })

      // 按匹配度排序
      scoredResumes.sort((a, b) => b.matchScore - a.matchScore)

      return {
        code: 20000,
        data: {
          reply,
          resumes: scoredResumes,
          totalMatches: matchedResumes.length
        }
      }
    }
  },

  // 保存对话记录
  {
    url: '/api/resume/save-chat',
    type: 'post',
    response: config => {
      const chatData = config.body
      const index = chatList.findIndex(chat => chat.id === chatData.id)
      
      if (index > -1) {
        chatList[index] = chatData
      } else {
        chatList.unshift(chatData)
      }

      return {
        code: 20000,
        data: 'success'
      }
    }
  },

  // 获取简历详情
  {
    url: '/resume/detail/\\d+',
    type: 'get',
    response: ({ url, method, query }) => {
      // 添加调试日志
      console.log('Mock request:', { url, method, query })

      try {
        // 从 query 中获取 id
        const id = parseInt(query.id)
        console.log('Looking for resume with ID:', id)

        // 从简历列表中查找详细信息
        const resume = resumes.find(item => item.id === id)
        console.log('Found resume:', resume)
        
        if (!resume) {
          console.warn('Resume not found for ID:', id)
          return {
            code: 50404,
            message: '简历不存在'
          }
        }

        return {
          code: 20000,
          data: resume
        }
      } catch (error) {
        console.error('Error in resume detail handler:', error)
        return {
          code: 50500,
          message: '服务器内部错误'
        }
      }
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

// 先定义 resumes 数组
const resumes = [
  {
    id: 1,
    name: '张三',
    title: '高级Java开发工程师',
    gender: '男',
    age: 28,
    phone: '13800138001',
    email: 'zhangsan@example.com',
    location: '上海',
    experience: 5,
    education: '本科',
    skills: ['Java', 'Spring Boot', 'MySQL', 'Redis', 'Microservices'],
    workExperience: [
      {
        period: '2020-2024',
        company: '阿里巴巴科技有限公司',
        position: '高级Java开发工程师',
        description: '负责公司核心电商系统的开发和维护，主导多个重要项目的技术方案设计和实现。',
        achievements: [
          '优化系统性能，将接口响应时间降低50%',
          '设计并实现分布式缓存方案，提升系统稳定性',
          '带领团队完成微服务架构转型'
        ]
      },
      {
        period: '2018-2020',
        company: '腾讯科技有限公司',
        position: 'Java开发工程师',
        description: '参与支付系统的开发和维护，负责核心模块的代码重构。',
        achievements: [
          '实现支付系统的性能监控平台',
          '获得年度最佳员工称号'
        ]
      }
    ],
    educationDetail: [
      {
        period: '2014-2018',
        school: '浙江大学',
        major: '计算机科学与技术',
        degree: '本科',
        achievements: [
          '获得校级奖学金',
          '参与多个开源项目的开发'
        ]
      }
    ],
    projects: [
      {
        name: '电商平台微服务改造项目',
        period: '2022-2023',
        description: '将传统单体应用拆分为微服务架构，提升系统的可扩展性和维护性。',
        responsibility: '负责整体技术方案设计，核心服务的拆分和实现，团队协调和进度把控。'
      },
      {
        name: '支付系统重构项目',
        period: '2019-2020',
        description: '对历史遗留系统进行重构，提升代码质量和系统性能。',
        responsibility: '负责支付核心模块的重构，引入设计模式，实现代码解耦。'
      }
    ],
    selfEvaluation: '拥有扎实的Java基础和丰富的分布式系统开发经验，对微服务架构有深入理解。善于解决技术难题，具有良好的团队协作能力。热爱技术，持续学习，期望在技术领域不断突破。',
    starred: false
  },
  {
    id: 2,
    name: '李四',
    title: '前端开发工程师',
    gender: '女',
    age: 26,
    phone: '13800138002',
    email: 'lisi@example.com',
    location: '北京',
    experience: 3,
    education: '硕士',
    skills: ['Vue', 'React', 'JavaScript', 'Node.js', 'TypeScript'],
    workExperience: [
      {
        period: '2021-2024',
        company: '字节跳动科技有限公司',
        position: '前端开发工程师',
        description: '负责公司内部管理系统的前端开发，参与多个项目的技术选型和架构设计。',
        achievements: [
          '构建前端组件库，提升开发效率30%',
          '推动前端自动化测试的落地'
        ]
      }
    ],
    educationDetail: [
      {
        period: '2018-2021',
        school: '北京大学',
        major: '软件工程',
        degree: '硕士',
        achievements: [
          '发表学术论文2篇',
          '参与国家级科研项目'
        ]
      }
    ],
    projects: [
      {
        name: '企业级中后台前端框架',
        period: '2022-2023',
        description: '基于Vue3和TypeScript开发的企业级前端框架，包含丰富的业务组件。',
        responsibility: '负责框架的核心功能开发，组件库设计，文档编写。'
      }
    ],
    selfEvaluation: '具有扎实的前端开发功底，对现代前端框架和工具链有深入理解。追求代码质量，注重用户体验，有较强的产品意识。',
    starred: false
  },
  {
    id: 3,
    name: '王五',
    title: 'Python开发工程师',
    gender: '男',
    age: 30,
    phone: '13800138003',
    email: 'wangwu@example.com',
    location: '广州',
    experience: 4,
    education: '本科',
    skills: ['Python', 'Django', 'Flask', 'MongoDB', 'Redis'],
    workExperience: [
      {
        period: '2020-2024',
        company: '腾讯科技有限公司',
        position: 'Python开发工程师',
        description: '负责公司内部管理系统的前端开发，参与多个项目的技术选型和架构设计。',
        achievements: [
          '构建前端组件库，提升开发效率30%',
          '推动前端自动化测试的落地'
        ]
      }
    ],
    educationDetail: [
      {
        period: '2016-2020',
        school: '北京大学',
        major: '计算机科学与技术',
        degree: '本科',
        achievements: [
          '获得校级奖学金',
          '参与多个开源项目的开发'
        ]
      }
    ],
    projects: [
      {
        name: '电商平台微服务改造项目',
        period: '2022-2023',
        description: '将传统单体应用拆分为微服务架构，提升系统的可扩展性和维护性。',
        responsibility: '负责整体技术方案设计，核心服务的拆分和实现，团队协调和进度把控。'
      }
    ],
    selfEvaluation: '拥有扎实的Python基础和丰富的分布式系统开发经验，对微服务架构有深入理解。善于解决技术难题，具有良好的团队协作能力。热爱技术，持续学习，期望在技术领域不断突破。',
    starred: false
  },
  {
    id: 4,
    name: '赵六',
    title: '全栈开发工程师',
    gender: '女',
    age: 29,
    phone: '13800138004',
    email: 'zhaoliu@example.com',
    location: '北京',
    experience: 5,
    education: '本科',
    skills: ['Java', 'Vue', 'MySQL', 'Spring Boot', 'JavaScript'],
    workExperience: [
      {
        period: '2020-2024',
        company: '字节跳动科技有限公司',
        position: '全栈开发工程师',
        description: '负责公司内部管理系统的前端开发，参与多个项目的技术选型和架构设计。',
        achievements: [
          '构建前端组件库，提升开发效率30%',
          '推动前端自动化测试的落地'
        ]
      }
    ],
    educationDetail: [
      {
        period: '2015-2019',
        school: '清华大学',
        major: '计算机科学与技术',
        degree: '本科',
        achievements: [
          '获得校级奖学金',
          '参与多个开源项目的开发'
        ]
      }
    ],
    projects: [
      {
        name: '电商平台微服务改造项目',
        period: '2022-2023',
        description: '将传统单体应用拆分为微服务架构，提升系统的可扩展性和维护性。',
        responsibility: '负责整体技术方案设计，核心服务的拆分和实现，团队协调和进度把控。'
      }
    ],
    selfEvaluation: '拥有扎实的全栈开发功底和丰富的分布式系统开发经验，对微服务架构有深入理解。善于解决技术难题，具有良好的团队协作能力。热爱技术，持续学习，期望在技术领域不断突破。',
    starred: false
  },
  {
    id: 5,
    name: '钱七',
    title: '后端开发工程师',
    gender: '男',
    age: 32,
    phone: '13800138005',
    email: 'qianqi@example.com',
    location: '上海',
    experience: 3,
    education: '硕士',
    skills: ['Java', 'Spring Cloud', 'MySQL', 'Redis', 'Docker'],
    workExperience: [
      {
        period: '2021-2024',
        company: '腾讯科技有限公司',
        position: '后端开发工程师',
        description: '负责公司内部管理系统的前端开发，参与多个项目的技术选型和架构设计。',
        achievements: [
          '构建前端组件库，提升开发效率30%',
          '推动前端自动化测试的落地'
        ]
      }
    ],
    educationDetail: [
      {
        period: '2018-2021',
        school: '北京大学',
        major: '软件工程',
        degree: '硕士',
        achievements: [
          '发表学术论文2篇',
          '参与国家级科研项目'
        ]
      }
    ],
    projects: [
      {
        name: '电商平台微服务改造项目',
        period: '2022-2023',
        description: '将传统单体应用拆分为微服务架构，提升系统的可扩展性和维护性。',
        responsibility: '负责整体技术方案设计，核心服务的拆分和实现，团队协调和进度把控。'
      }
    ],
    selfEvaluation: '拥有扎实的Java基础和丰富的分布式系统开发经验，对微服务架构有深入理解。善于解决技术难题，具有良好的团队协作能力。热爱技术，持续学习，期望在技术领域不断突破。',
    starred: false
  },
  {
    id: 6,
    name: '孙八',
    title: '前端开发工程师',
    gender: '女',
    age: 27,
    phone: '13800138006',
    email: 'sunba@example.com',
    location: '北京',
    experience: 4,
    education: '本科',
    skills: ['Vue', 'React', 'TypeScript', 'Webpack', 'Node.js'],
    workExperience: [
      {
        period: '2020-2024',
        company: '字节跳动科技有限公司',
        position: '前端开发工程师',
        description: '负责公司内部管理系统的前端开发，参与多个项目的技术选型和架构设计。',
        achievements: [
          '构建前端组件库，提升开发效率30%',
          '推动前端自动化测试的落地'
        ]
      }
    ],
    educationDetail: [
      {
        period: '2016-2020',
        school: '北京大学',
        major: '软件工程',
        degree: '本科',
        achievements: [
          '获得校级奖学金',
          '参与多个开源项目的开发'
        ]
      }
    ],
    projects: [
      {
        name: '电商平台微服务改造项目',
        period: '2022-2023',
        description: '将传统单体应用拆分为微服务架构，提升系统的可扩展性和维护性。',
        responsibility: '负责整体技术方案设计，核心服务的拆分和实现，团队协调和进度把控。'
      }
    ],
    selfEvaluation: '具有扎实的前端开发功底和丰富的分布式系统开发经验，对微服务架构有深入理解。善于解决技术难题，具有良好的团队协作能力。热爱技术，持续学习，期望在技术领域不断突破。',
    starred: false
  }
]

// 然后再定义 chatList
const chatList = [
  {
    id: 1,
    title: '寻找Java高级开发工程师',
    createTime: '2024-03-15 14:30:00',
    messages: [
      {
        id: 11,
        role: 'user',
        content: '需要一位5年以上Java开发经验，精通Spring Cloud微服务架构的高级工程师',
        timestamp: '2024-03-15 14:30:00'
      },
      {
        id: 12,
        role: 'assistant',
        content: '我找到了2份非常匹配的简历。这些候选人都具有丰富的Java开发经验和微服务架构实践。',
        timestamp: '2024-03-15 14:30:02',
        resumes: [
          resumes[0], // 张三
          resumes[4]  // 钱七
        ]
      },
      {
        id: 13,
        role: 'user',
        content: '他们都有Docker经验吗？',
        timestamp: '2024-03-15 14:31:00'
      },
      {
        id: 14,
        role: 'assistant',
        content: '在这两位候选人中，钱七有Docker相关经验。他目前在腾讯负责容器化相关工作。您想了解更多细节吗？',
        timestamp: '2024-03-15 14:31:02',
        resumes: [
          resumes[4]  // 钱七
        ]
      }
    ]
  },
  {
    id: 2,
    title: '招聘全栈开发工程师',
    createTime: '2024-03-14 10:15:00',
    messages: [
      {
        id: 21,
        role: 'user',
        content: '需要招聘一位全栈开发工程师，要求同时熟悉Java后端和Vue前端开发',
        timestamp: '2024-03-14 10:15:00'
      },
      {
        id: 22,
        role: 'assistant',
        content: '为您找到一位非常合适的候选人。赵六是一位经验丰富的全栈工程师，同时精通Java后端和Vue前端开发。',
        timestamp: '2024-03-14 10:15:02',
        resumes: [
          resumes[3]  // 赵六
        ]
      }
    ]
  },
  {
    id: 3,
    title: '前端开发团队招聘',
    createTime: '2024-03-13 16:45:00',
    messages: [
      {
        id: 31,
        role: 'user',
        content: '我们在组建前端开发团队，需要有Vue和React经验的工程师',
        timestamp: '2024-03-13 16:45:00'
      },
      {
        id: 32,
        role: 'assistant',
        content: '我找到了3位优秀的前端开发工程师，他们都具有Vue和React的项目经验。',
        timestamp: '2024-03-13 16:45:02',
        resumes: [
          resumes[1],  // 李四
          resumes[5],  // 孙八
          resumes[3]   // 赵六
        ]
      },
      {
        id: 33,
        role: 'user',
        content: '谁的TypeScript经验最丰富？',
        timestamp: '2024-03-13 16:46:00'
      },
      {
        id: 34,
        role: 'assistant',
        content: '李四和孙八都有丰富的TypeScript经验。特别是李四，在字节跳动主导过基于TypeScript的前端框架开发。',
        timestamp: '2024-03-13 16:46:02',
        resumes: [
          resumes[1],  // 李四
          resumes[5]   // 孙八
        ]
      }
    ]
  },
  {
    id: 4,
    title: 'Python开发工程师招聘',
    createTime: '2024-03-12 09:20:00',
    messages: [
      {
        id: 41,
        role: 'user',
        content: '寻找Python开发工程师，最好有Django和Flask经验',
        timestamp: '2024-03-12 09:20:00'
      },
      {
        id: 42,
        role: 'assistant',
        content: '找到了一位非常匹配的候选人。王五同时具有Django和Flask的开发经验，并且熟悉MongoDB数据库。',
        timestamp: '2024-03-12 09:20:02',
        resumes: [
          resumes[2]  // 王五
        ]
      }
    ]
  },
  {
    id: 5,
    title: '高学历Java开发',
    createTime: '2024-03-11 11:30:00',
    messages: [
      {
        id: 51,
        role: 'user',
        content: '需要一位硕士学历的Java开发工程师',
        timestamp: '2024-03-11 11:30:00'
      },
      {
        id: 52,
        role: 'assistant',
        content: '为您找到一位符合要求的候选人。钱七是硕士学历，专注于Java后端开发，特别擅长微服务架构。',
        timestamp: '2024-03-11 11:30:02',
        resumes: [
          resumes[4]  // 钱七
        ]
      },
      {
        id: 53,
        role: 'user',
        content: '他有什么项目经验？',
        timestamp: '2024-03-11 11:31:00'
      },
      {
        id: 54,
        role: 'assistant',
        content: '钱七在腾讯主导过多个微服务项目，包括电商平台的微服务改造。他有丰富的Spring Cloud和Docker经验。',
        timestamp: '2024-03-11 11:31:02',
        resumes: [
          resumes[4]  // 钱七
        ]
      }
    ]
  }
]

// 添加计算简历匹配度的函数
function calculateMatchScore(resume, message) {
  let score = 0
  const keywords = message.toLowerCase().split(/\s+/)
  
  // 技能匹配度评分
  keywords.forEach(keyword => {
    resume.skills.forEach(skill => {
      if (skill.toLowerCase().includes(keyword)) {
        score += 10
      }
    })
  })
  
  // 职位匹配度评分
  keywords.forEach(keyword => {
    if (resume.title.toLowerCase().includes(keyword)) {
      score += 8
    }
  })
  
  // 经验年限匹配度评分
  const yearPattern = /(\d+)年/
  const messageYears = message.match(yearPattern)
  if (messageYears) {
    const targetYears = parseInt(messageYears[1])
    const diff = Math.abs(resume.experience - targetYears)
    if (diff === 0) {
      score += 10
    } else if (diff <= 2) {
      score += 5
    }
  }
  
  return score
} 