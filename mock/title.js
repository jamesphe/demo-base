const Mock = require('mockjs')

const titleList = Mock.mock({
  'items|30': [{
    id: '@increment',
    // 职称编码: 2位学科类别+4位序号，如：JS0001(教师系列)，GZ0002(工职系列)
    'code|1': [
      'JS0001', 'JS0002', 'JS0003', // 教师系列
      'GZ0001', 'GZ0002', 'GZ0003', // 工职系列
      'ZH0001', 'ZH0002', 'ZH0003'  // 综合系列
    ],
    // 职称名称
    'name|1': [
      '正高级讲师', '高级讲师', '讲师', '助教', // 教师系列
      '高级实验师', '实验师', '助理实验师', // 实验系列
      '高级工程师', '工程师', '助理工程师', // 工程系列
      '研究员', '副研究员', '助理研究员', // 研究系列
      '高级技师', '技师', '助理技师'  // 技能系列
    ],
    // 职称等级: 1-正高级 2-副高级 3-中级 4-初级
    'level|1': ['1', '2', '3', '4'],
    // 职称类别: 1-教师系列 2-实验系列 3-工程系列 4-研究系列 5-技能系列
    'category|1': ['1', '2', '3', '4', '5'],
    // 状态: 1-启用 0-停用
    'status|1': [0, 1],
    // 创建时间
    createTime: '@datetime("yyyy-MM-dd HH:mm:ss")',
    // 备注
    remark: '@csentence(10, 20)',
    // 所需学历
    'education|1': ['博士', '硕士', '本科', '专科'],
    // 所需工作年限
    'workYear|1': ['5年以上', '3年以上', '2年以上', '1年以上'],
    // 评审条件
    'requirement': '@cparagraph(1, 2)',
    // 聘任年限
    'appointmentPeriod|1': ['长期', '3年', '2年', '1年']
  }]
})

// 职称等级映射
const levelMap = {
  '1': '正高级',
  '2': '副高级',
  '3': '中级',
  '4': '初级'
}

// 职称类别映射
const categoryMap = {
  '1': '教师系列',
  '2': '实验系列',
  '3': '工程系列',
  '4': '研究系列',
  '5': '技能系列'
}

module.exports = [
  {
    url: '/vue-element-admin/title/list',
    type: 'get',
    response: config => {
      console.log('Mock title list request:', config)
      const { keyword, page = 1, limit = 20, level, category, education } = config.query

      let mockList = titleList.items

      // 按职称名称搜索
      if (keyword) {
        mockList = mockList.filter(item => item.name.includes(keyword))
      }

      // 按职称等级筛选
      if (level) {
        mockList = mockList.filter(item => item.level === level)
      }

      // 按职称类别筛选
      if (category) {
        mockList = mockList.filter(item => item.category === category)
      }

      // 按学历要求筛选
      if (education) {
        mockList = mockList.filter(item => item.education === education)
      }

      // 分页
      const pageList = mockList.filter((item, index) => index < limit * page && index >= limit * (page - 1))

      // 转换等级和类别的显示
      pageList.forEach(item => {
        item.levelName = levelMap[item.level]
        item.categoryName = categoryMap[item.category]
      })

      return {
        code: 20000,
        data: {
          total: mockList.length,
          items: pageList
        }
      }
    }
  },

  {
    url: '/vue-element-admin/title/create',
    type: 'post',
    response: config => {
      const { code, name } = config.body
      
      // 校验职称编码是否已存在
      const isExist = titleList.items.some(item => item.code === code)
      if (isExist) {
        return {
          code: 50000,
          message: '职称编码已存在'
        }
      }

      titleList.items.unshift({
        id: Mock.mock('@increment'),
        code,
        name,
        ...config.body,
        createTime: Mock.mock('@datetime("yyyy-MM-dd HH:mm:ss")')
      })

      return {
        code: 20000,
        data: 'success'
      }
    }
  },

  {
    url: '/vue-element-admin/title/update',
    type: 'post',
    response: config => {
      const { id, code, name } = config.body
      
      // 校验职称编码是否已存在(排除自身)
      const isExist = titleList.items.some(item => item.code === code && item.id !== id)
      if (isExist) {
        return {
          code: 50000,
          message: '职称编码已存在'
        }
      }

      const item = titleList.items.find(item => item.id === id)
      if (item) {
        Object.assign(item, config.body)
      }

      return {
        code: 20000,
        data: 'success'
      }
    }
  }
] 