const Mock = require('mockjs')

// 候选人状态枚举
const statusEnum = {
  pending: '待处理',
  interviewing: '面试中',
  hired: '已录用',
  rejected: '已拒绝'
}

// 生成候选人列表数据
const candidateList = Mock.mock({
  'items|30': [{
    id: '@increment',
    name: '@cname',
    phone: /^1[3-9]\d{9}$/,
    email: '@email',
    education: '@pick(["大专", "本科", "硕士", "博士"])',
    workYears: '@integer(0, 15)',
    status: '@pick(["pending", "interviewing", "hired", "rejected"])',
    'skills|2-4': ['@pick(["Java", "Python", "JavaScript", "Vue", "React", "Node.js", "MySQL", "MongoDB", "Docker"])'],
    createTime: '@datetime'
  }]
})

// 生成评估记录列表数据
const evaluationList = Mock.mock({
  'items|20': [{
    id: '@increment',
    candidateId: '@integer(1, 30)',
    candidateName: '@cname',
    // 技术评估项
    technicalScore: '@float(2, 5, 1, 1)',
    'technicalItems|4': [{
      name: '@pick(["编程能力", "架构设计", "问题解决", "代码质量", "技术广度", "学习能力"])',
      score: '@float(2, 5, 1, 1)',
      comment: '@sentence(5, 10)'
    }],
    // 综合素质评估
    communicationScore: '@float(2, 5, 1, 1)',
    'softSkills|3': [{
      name: '@pick(["沟通表达", "团队协作", "抗压能力", "职业素养", "项目管理"])',
      score: '@float(2, 5, 1, 1)',
      comment: '@sentence(5, 10)'
    }],
    // 项目经验评估
    'projectExperience|2': [{
      name: '@ctitle(4, 8)项目',
      role: '@pick(["前端开发", "后端开发", "技术负责人", "全栈开发"])',
      contribution: '@sentence(10, 20)',
      highlight: '@sentence(8, 15)'
    }],
    // 综合评价
    overallRating: '@pick(["推荐", "待定", "不推荐"])',
    comment: '@paragraph(1, 3)',
    // 面试官信息
    evaluator: '@cname',
    evaluatorTitle: '@pick(["高级工程师", "技术专家", "技术总监", "架构师"])',
    evaluationTime: '@datetime("yyyy-MM-dd HH:mm:ss")',
    // 面试环节
    interviewRound: '@pick(["初试", "复试", "终试"])',
    duration: '@integer(30, 120)分钟',
    // 附加信息
    tags: '@pick(["成长潜力大", "经验丰富", "技术扎实", "沟通优秀", "团队协作好"], 1, 3)',
    salary: {
      current: '@integer(10, 30)k',
      expected: '@integer(15, 40)k'
    },
    status: '@pick(["待定", "通过", "未通过"])'
  }]
})

// 生成职位列表数据
const positionList = Mock.mock({
  'items|10': [{
    id: '@increment',
    name: '@pick(["前端开发工程师", "后端开发工程师", "全栈工程师", "DevOps工程师", "测试工程师", "产品经理", "UI设计师"])',
    department: '@pick(["技术部", "产品部", "设计部"])',
    requirement: '@sentence(20, 30)',
    'skills|3-5': ['@pick(["Java", "Python", "JavaScript", "Vue", "React", "Node.js", "MySQL", "MongoDB", "Docker"])'],
    workYears: '@integer(1, 5)',
    education: '@pick(["本科", "硕士"])',
    status: '@pick(["open", "closed"])'
  }]
})

// 生成候选人推荐列表数据
const recommendationList = Mock.mock({
  'items|10': [{
    id: '@increment',
    name: '@cname',
    // 匹配度相关
    matchRate: '@integer(60, 100)',
    'skillMatches|3-5': [{
      name: '@pick(["Java", "Python", "JavaScript", "Vue", "React", "Node.js", "MySQL", "MongoDB", "Docker"])',
      matchLevel: '@pick(["精通", "熟练", "了解"])',
      yearOfExperience: '@integer(1, 5)'
    }],
    // 工作经验
    workYears: '@integer(1, 8)',
    'workExperience|2-3': [{
      company: '@ctitle(4, 8)科技有限公司',
      position: '@pick(["高级工程师", "技术主管", "架构师", "开发工程师"])',
      period: '@integer(1, 3)年',
      description: '@paragraph(1, 2)'
    }],
    // 教育背景
    education: {
      degree: '@pick(["本科", "硕士", "博士"])',
      school: '@ctitle(4, 8)大学',
      major: '@pick(["计算机科学与技术", "软件工程", "信息工程", "通信工程"])',
      graduationYear: '@date("yyyy")'
    },
    // 项目经验
    'projects|2-3': [{
      name: '@ctitle(4, 8)项目',
      role: '@pick(["项目负责人", "核心开发", "技术主管"])',
      description: '@paragraph(1, 2)',
      'technologies|3-5': ['@pick(["Vue", "React", "Node.js", "MySQL", "Redis", "Docker", "Kubernetes"])']
    }],
    // 薪资信息
    salary: {
      current: '@integer(15, 35)k',
      expected: '@integer(20, 45)k'
    },
    // 求职意向
    jobIntention: {
      positions: '@pick(["前端开发", "后端开发", "全栈开发"], 1, 2)',
      cities: '@pick(["北京", "上海", "广州", "深圳", "杭州"], 1, 2)',
      availableTime: '@pick(["随时到岗", "一周内到岗", "一个月内到岗"])',
      jobStatus: '@pick(["在职-考虑机会", "在职-暂不考虑", "离职-正在找工作"])'
    },
    // 加分项
    highlights: '@pick(["技术博客", "开源项目", "技术专利", "技术分享"], 1, 3)',
    // 评价标签
    tags: '@pick(["技术过硬", "学习能力强", "团队协作好", "有管理经验", "有架构经验"], 2, 4)',
    // 推荐理由
    recommendReason: '@paragraph(1, 2)',
    // 更新时间
    updateTime: '@datetime("yyyy-MM-dd HH:mm:ss")'
  }]
})

// Mock API 接口
module.exports = [
  // 获取候选人列表
  {
    url: '/dev-api/vue-element-admin/candidate/list',
    type: 'get',
    response: config => {
      const { name, status, page = 1, limit = 10 } = config.query
      let items = candidateList.items

      // 按名称筛选
      if (name) {
        items = items.filter(item => item.name.includes(name))
      }

      // 按状态筛选
      if (status) {
        items = items.filter(item => item.status === status)
      }

      // 分页
      const start = (page - 1) * limit
      const end = start + limit

      return {
        code: 20000,
        data: {
          total: items.length,
          items: items.slice(start, end)
        }
      }
    }
  },

  // 获取评估列表
  {
    url: '/dev-api/vue-element-admin/candidate/evaluation/list',
    type: 'get',
    response: config => {
      const { name, status, page = 1, limit = 10 } = config.query
      let items = evaluationList.items

      // 按候选人名称筛选
      if (name) {
        items = items.filter(item => item.candidateName.includes(name))
      }

      // 按状态筛选
      if (status) {
        items = items.filter(item => item.status === status)
      }

      // 分页
      const start = (page - 1) * limit
      const end = start + limit

      return {
        code: 20000,
        data: {
          total: items.length,
          items: items.slice(start, end)
        }
      }
    }
  },

  // 获取评估详情
  {
    url: '/dev-api/vue-element-admin/candidate/evaluation/detail',
    type: 'get',
    response: config => {
      const { id } = config.query
      const evaluation = evaluationList.items.find(item => item.id === parseInt(id))
      
      return {
        code: 20000,
        data: evaluation
      }
    }
  },

  // 提交评估
  {
    url: '/dev-api/vue-element-admin/candidate/evaluation/create',
    type: 'post',
    response: config => {
      const { candidateId, evaluation } = config.body
      
      return {
        code: 20000,
        data: {
          message: '评估提交成功'
        }
      }
    }
  },

  // 获取职位列表
  {
    url: '/dev-api/vue-element-admin/position/list',
    type: 'get',
    response: config => {
      const { status } = config.query
      let items = positionList.items

      // 按状态筛选
      if (status) {
        items = items.filter(item => item.status === status)
      }

      return {
        code: 20000,
        data: {
          total: items.length,
          items
        }
      }
    }
  },

  // 获取推荐候选人列表
  {
    url: '/dev-api/vue-element-admin/candidate/recommendation/list',
    type: 'get',
    response: config => {
      const { positionId, matchRate, page = 1, limit = 10 } = config.query
      let items = recommendationList.items

      // 按匹配度筛选
      if (matchRate) {
        items = items.filter(item => item.matchRate >= parseInt(matchRate))
      }

      // 分页
      const start = (page - 1) * limit
      const end = start + limit

      return {
        code: 20000,
        data: {
          total: items.length,
          items: items.slice(start, end)
        }
      }
    }
  },

  // 获取推荐候选人详情
  {
    url: '/dev-api/vue-element-admin/candidate/recommendation/detail',
    type: 'get',
    response: config => {
      const { id } = config.query
      const recommendation = recommendationList.items.find(item => item.id === parseInt(id))
      
      if (!recommendation) {
        return {
          code: 50404,
          message: '候选人不存在'
        }
      }

      return {
        code: 20000,
        data: recommendation
      }
    }
  },

  // 联系候选人
  {
    url: '/dev-api/vue-element-admin/candidate/recommendation/contact',
    type: 'post',
    response: config => {
      const { id } = config.body
      
      return {
        code: 20000,
        data: {
          message: '操作成功',
          contact: Mock.mock({
            phone: /^1[3-9]\d{9}$/,
            email: '@email',
            wechat: /^[a-zA-Z][a-zA-Z\d_-]{5,19}$/
          })
        }
      }
    }
  }
] 