const Mock = require('mockjs')

// 定义托管单位和合作企业的可选值
const supportUnits = [
  '华为技术有限公司',
  '阿里巴巴集团',
  '腾讯科技有限公司',
  '浪潮集团有限公司',
  '中兴通讯股份有限公司',
  '联想集团有限公司',
  '新华三技术有限公司',
  '深信服科技股份有限公司',
  '科大讯飞股份有限公司',
  '东软集团有限公司'
]

const partnerCompanies = [
  '华为技术有限公司',
  '阿里云计算有限公司',
  '腾讯云计算有限公司',
  '浪潮软件集团有限公司',
  '中兴软创科技有限公司',
  '联想（北京）有限公司',
  '新华三信息技术有限公司',
  '深信服信息技术有限公司',
  '科大讯飞华东研究院',
  '东软教育科技有限公司'
]

const baseList = []
const count = 20

for (let i = 0; i < count; i++) {
  baseList.push(Mock.mock({
    id: '@increment',
    'name|1': [
      '机械工程实训基地',
      '电子信息实训基地', 
      '计算机科学实训基地',
      '自动化控制实训基地',
      '物联网技术实训基地'
    ],
    deptId: '@integer(1, 10)',
    'deptName|1': [
      '信息工程学院',
      '机械工程学院',
      '电气工程学院',
      '自动化学院'
    ],
    createTime: '@date("yyyy-MM-dd")',
    'supportUnit|1': supportUnits,  // 从托管单位列表中随机选择
    'majors|1': [
      '软件工程,计算机科学与技术',
      '机械设计制造,机械自动化',
      '电子信息工程,通信工程',
      '自动化,电气工程及其自动化'
    ],
    'partner|1': partnerCompanies,  // 从合作企业列表中随机选择
    'typeCode|1': [
      '01-校内实训基地',
      '02-校外实训基地',
      '03-生产性实训基地'
    ],
    manager: '@cname',
    contact: '1@integer(3000000000,9999999999)',
    description: '@cparagraph(1)',
    roomCount: '@integer(3,10)',
    equipmentCount: '@integer(20,100)'
  }))
}

// 实训室列表数据
const trainingRooms = [
  {
    id: 1,
    name: '软件开发实训室A101',
    baseId: 1,
    baseName: '计算机科学实训基地',
    capacity: 50,
    status: 'available', // 修改状态格式
    deviceCount: 51, // 添加设备数量
    equipment: '电脑50台，投影仪1台',
    description: '主要用于软件开发课程实训',
    location: '教学楼A区一层',
    manager: '张老师',
    createTime: '2024-01-15 08:00:00'
  },
  {
    id: 2,
    name: '网络工程实训室B201',
    baseId: 1,
    baseName: '计算机科学实训基地',
    capacity: 40,
    status: 'available',
    deviceCount: 40, // 服务器+交换机+路由器数量
    equipment: '服务器10台，交换机20台，路由器10台',
    description: '用于网络配置与管理实训',
    location: '教学楼B区二层',
    manager: '李老师',
    createTime: '2024-01-16 09:00:00'
  },
  {
    id: 3,
    name: '云计算实训室C301',
    baseId: 2,
    baseName: '电子信息实训基地',
    capacity: 45,
    status: 'maintenance',
    deviceCount: 10,
    equipment: '服务器集群，存储阵列',
    description: '适用于云计算和虚拟化技术实训',
    location: '教学楼C区三层',
    manager: '王老师',
    createTime: '2024-01-17 10:00:00'
  },
  {
    id: 4,
    name: '人工智能实训室D401',
    baseId: 3,
    baseName: '人工智能实训基地',
    capacity: 35,
    status: 'available',
    deviceCount: 25,
    equipment: 'GPU工作站20台，深度学习服务器5台',
    description: '用于机器学习和深度学习实训',
    location: '教学楼D区四层',
    manager: '刘老师',
    createTime: '2024-01-18 11:00:00'
  },
  {
    id: 5,
    name: '物联网实训室E501',
    baseId: 4,
    baseName: '物联网技术实训基地',
    capacity: 30,
    status: 'available',
    deviceCount: 100,
    equipment: '各类传感器，开发板，智能设备',
    description: '物联网应用开发与测试实训',
    location: '教学楼E区五层',
    manager: '陈老师',
    createTime: '2024-01-19 12:00:00'
  }
]

const baseAPI = [
  {
    url: '/base/list',
    type: 'get',
    response: config => {
      const { keyword, page = 1, limit = 10 } = config.query

      const mockList = baseList.filter(item => {
        if (keyword && item.name.indexOf(keyword) < 0) return false
        return true
      })

      const pageList = mockList.filter((item, index) => index < limit * page && index >= limit * (page - 1))

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
    url: '/base',
    type: 'post',
    response: config => {
      const { 
        name, 
        deptName, 
        supportUnit, 
        majors, 
        partner, 
        typeCode,
        manager, 
        contact, 
        description 
      } = config.body
      
      baseList.push(Mock.mock({
        id: '@increment',
        name,
        deptId: '@integer(1, 10)',
        deptName,
        createTime: '@date("yyyy-MM-dd")',
        supportUnit,
        majors,
        partner,
        typeCode,
        manager,
        contact,
        description,
        roomCount: '@integer(3,10)',
        equipmentCount: '@integer(20,100)'
      }))

      return {
        code: 20000,
        data: '添加成功'
      }
    }
  },

  {
    url: '/base/\\d+',
    type: 'put',
    response: config => {
      const { id } = config.body
      const index = baseList.findIndex(item => item.id === id)
      if (index > -1) {
        baseList[index] = Object.assign({}, baseList[index], config.body)
      }

      return {
        code: 20000,
        data: '更新成功'
      }
    }
  },

  {
    url: '/base/\\d+',
    type: 'delete',
    response: config => {
      const id = config.url.split('/').pop()
      const index = baseList.findIndex(item => item.id === parseInt(id))
      if (index > -1) {
        baseList.splice(index, 1)
      }

      return {
        code: 20000,
        data: '删除成功'
      }
    }
  },

  // 获取实训室列表（支持按实训基地筛选）
  {
    url: '/api/training-rooms',
    type: 'get',
    response: config => {
      const { baseId, name, status, sort, order } = config.query
      let filteredRooms = trainingRooms
      
      // 按基地筛选
      if (baseId) {
        filteredRooms = filteredRooms.filter(room => room.baseId === parseInt(baseId))
      }
      
      // 按名称搜索
      if (name) {
        filteredRooms = filteredRooms.filter(room => room.name.includes(name))
      }
      
      // 按状态筛选
      if (status) {
        filteredRooms = filteredRooms.filter(room => room.status === status)
      }
      
      // 排序
      if (sort && order) {
        filteredRooms.sort((a, b) => {
          if (order === 'ascending') {
            return a[sort] - b[sort]
          } else {
            return b[sort] - a[sort]
          }
        })
      }
      
      return {
        code: 20000,
        data: {
          total: filteredRooms.length,
          items: filteredRooms
        }
      }
    }
  },
  
  // 获取单个实训室详情
  {
    url: '/api/training-rooms/\\d+',
    type: 'get',
    response: config => {
      const id = parseInt(config.url.split('/').pop())
      const room = trainingRooms.find(item => item.id === id)
      return {
        code: 20000,
        data: room
      }
    }
  }
]

module.exports = baseAPI 