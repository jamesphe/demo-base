const Mock = require('mockjs')

// 生成岗位数据
const generatePositions = () => {
  // 教师岗位
  const teacherPositions = [
    { name: '教授', code: 'JS001', type: 1 },
    { name: '副教授', code: 'FJS01', type: 1 },
    { name: '讲师', code: 'JK001', type: 1 },
    { name: '助教', code: 'ZJ001', type: 1 }
  ]

  // 行政管理岗位
  const adminPositions = [
    { name: '院长', code: 'YZ001', type: 2 },
    { name: '副院长', code: 'FYZ01', type: 2 },
    { name: '处长', code: 'CZ001', type: 2 },
    { name: '科长', code: 'KZ001', type: 2 },
    { name: '职员', code: 'ZY001', type: 2 }
  ]

  // 教辅岗位
  const supportPositions = [
    { name: '实验室管理员', code: 'SY001', type: 3 },
    { name: '图书管理员', code: 'TS001', type: 3 },
    { name: '教务员', code: 'JW001', type: 3 },
    { name: '辅导员', code: 'FD001', type: 3 }
  ]

  // 工勤岗位
  const logisticsPositions = [
    { name: '保安', code: 'BA001', type: 4 },
    { name: '保洁', code: 'BJ001', type: 4 },
    { name: '维修工', code: 'WX001', type: 4 },
    { name: '绿化工', code: 'LH001', type: 4 }
  ]

  const allPositions = [
    ...teacherPositions,
    ...adminPositions,
    ...supportPositions,
    ...logisticsPositions
  ]

  return allPositions.map((pos, index) => ({
    id: index + 1,
    name: pos.name,
    code: pos.code,
    type: pos.type, // 1-教师岗位 2-行政岗位 3-教辅岗位 4-工勤岗位
    typeName: ['', '教师岗位', '行政岗位', '教辅岗位', '工勤岗位'][pos.type],
    description: Mock.mock('@cparagraph(1)'),
    requirements: Mock.mock('@cparagraph(1)'),
    duties: Mock.mock('@cparagraph(1)'),
    orderNum: index + 1,
    status: Mock.Random.integer(0, 1),
    createTime: Mock.Random.datetime(),
    updateTime: Mock.Random.datetime(),
    remark: Mock.mock('@cparagraph(1)')
  }))
}

const positionList = generatePositions()

// 岗位类型选项
const positionTypes = [
  { value: 1, label: '教师岗位' },
  { value: 2, label: '行政岗位' },
  { value: 3, label: '教辅岗位' },
  { value: 4, label: '工勤岗位' }
]

module.exports = [
  // 获取岗位列表
  {
    url: '/vue-element-admin/position/list',
    type: 'get',
    response: config => {
      console.log('Mock position list request:', config.query)
      const { name, code, type, status, pageNum = 1, pageSize = 10 } = config.query

      let mockList = positionList.filter(item => {
        if (name && !item.name.includes(name)) return false
        if (code && !item.code.includes(code)) return false
        if (type && item.type !== parseInt(type)) return false
        if (status !== '' && status !== undefined && item.status !== parseInt(status)) return false
        return true
      })

      const startIndex = (pageNum - 1) * pageSize
      const endIndex = startIndex + parseInt(pageSize)
      const pageList = mockList.slice(startIndex, endIndex)

      // 确保返回正确的数据结构
      const result = {
        code: 20000,
        data: {
          total: mockList.length,
          items: pageList.map(item => ({
            id: item.id,
            name: item.name,
            code: item.code,
            type: Number(item.type),
            typeName: item.typeName,
            description: item.description,
            requirements: item.requirements,
            duties: item.duties,
            orderNum: Number(item.orderNum),
            status: Number(item.status),
            createTime: item.createTime,
            updateTime: item.updateTime
          }))
        }
      }

      console.log('Mock response:', result)
      return result
    }
  },

  // 获取岗位类型选项
  {
    url: '/vue-element-admin/position/types',
    type: 'get',
    response: _ => {
      return {
        code: 20000,
        data: positionTypes
      }
    }
  },

  // 获取岗位详情
  {
    url: '/vue-element-admin/position/\\d+',
    type: 'get',
    response: config => {
      const { url } = config
      const id = parseInt(url.match(/\/position\/(\d+)/)[1])
      const position = positionList.find(item => item.id === id)
      return {
        code: 20000,
        data: position
      }
    }
  },

  // 新增岗位
  {
    url: '/vue-element-admin/position',
    type: 'post',
    response: config => {
      const { name, code } = config.body
      
      // 检查是否存在重复
      const isNameExist = positionList.some(item => item.name === name)
      const isCodeExist = positionList.some(item => item.code === code)
      
      if (isNameExist) {
        return {
          code: 20001,
          message: '岗位名称已存在'
        }
      }
      if (isCodeExist) {
        return {
          code: 20001,
          message: '岗位编码已存在'
        }
      }

      return {
        code: 20000,
        data: 'success'
      }
    }
  },

  // 修改岗位
  {
    url: '/vue-element-admin/position',
    type: 'put',
    response: config => {
      const { id, name, code } = config.body
      
      // 检查是否存在重复(排除自身)
      const isNameExist = positionList.some(item => item.name === name && item.id !== id)
      const isCodeExist = positionList.some(item => item.code === code && item.id !== id)
      
      if (isNameExist) {
        return {
          code: 20001,
          message: '岗位名称已存在'
        }
      }
      if (isCodeExist) {
        return {
          code: 20001,
          message: '岗位编码已存在'
        }
      }

      return {
        code: 20000,
        data: 'success'
      }
    }
  },

  // 删除岗位
  {
    url: '/vue-element-admin/position/\\d+',
    type: 'delete',
    response: {
      code: 20000,
      data: 'success'
    }
  }
] 