const Mock = require('mockjs')

// 先定义一个自增ID计数器
let autoIncrementId = 0

const equipmentList = []
const count = 20

const roomList = [
  { id: 1, name: '计算机基础实训室' },
  { id: 2, name: '网络工程实训室' },
  { id: 3, name: '电子技术实训室' },
  { id: 4, name: '机械加工实训室' },
  { id: 5, name: '自动化控制实训室' }
]

const managerList = [
  { id: 1, name: '张三' },
  { id: 2, name: '李四' },
  { id: 3, name: '王五' },
  { id: 4, name: '赵六' }
]

console.log('Initializing mock data...')

// 生成模拟数据
for (let i = 0; i < count; i++) {
  const room = roomList[Math.floor(Math.random() * roomList.length)]
  const manager = managerList[Math.floor(Math.random() * managerList.length)]
  
  // 手动控制 ID 自增
  autoIncrementId++
  
  const mockItem = {
    id: autoIncrementId,
    equipmentCode: `EQ${String(100000 + autoIncrementId).slice(1)}`,
    name: Mock.mock('@cword(3,5)') + '设备',
    type: Mock.Random.pick(['计算机', '网络设备', '机械设备', '电子设备', '测量设备']),
    model: `${Mock.Random.string('upper', 5)}${Mock.Random.integer(100, 999)}`,
    status: Mock.Random.pick(['normal', 'maintenance', 'scrapped']),
    purchaseDate: Mock.Random.date(),
    price: Mock.Random.float(1000, 100000, 2, 2),
    quantity: Mock.Random.integer(1, 50),
    lifespan: Mock.Random.integer(3, 10),
    manufacturer: Mock.mock('@cword(5,10)') + '公司',
    supplier: Mock.mock('@cword(5,10)') + '科技有限公司',
    roomId: room.id,
    roomName: room.name,
    manager: manager.name,
    managerId: manager.id,
    remark: Mock.mock('@cparagraph(1, 2)'),
    createTime: Mock.Random.datetime(),
    updateTime: Mock.Random.datetime()
  }
  
  equipmentList.push(mockItem)
}

console.log(`Generated ${equipmentList.length} mock equipment items:`, equipmentList)

// 生成设备申报数据
const approvalList = []
const approvalCount = 15

for (let i = 0; i < approvalCount; i++) {
  const mockApproval = {
    id: Mock.mock('@increment(1)'),
    applyCode: `AP${String(100000 + i + 1).slice(1)}`,
    equipmentName: Mock.mock('@cword(3,5)') + '设备',
    model: `${Mock.Random.string('upper', 5)}${Mock.Random.integer(100, 999)}`,
    price: Mock.Random.float(1000, 100000, 2, 2),
    quantity: Mock.Random.integer(1, 20),
    applyReason: Mock.mock('@cparagraph(1)'),
    applicant: Mock.Random.pick(['张三', '李四', '王五', '赵六']),
    applyDate: Mock.Random.date('yyyy-MM-dd'),
    status: Mock.Random.pick(['pending', 'approved', 'rejected']),
    rejectReason: '',
    createTime: Mock.Random.datetime(),
    updateTime: Mock.Random.datetime()
  }
  
  if (mockApproval.status === 'rejected') {
    mockApproval.rejectReason = Mock.mock('@cparagraph(1)')
  }
  
  approvalList.push(mockApproval)
}

module.exports = [
  {
    url: '/equipment/list',
    type: 'get',
    response: config => {
      const { keyword, type, status, page = 1, limit = 10 } = config.query

      let mockList = equipmentList.filter(item => {
        if (keyword && !item.name.includes(keyword) && !item.equipmentCode.includes(keyword)) return false
        if (type && item.type !== type) return false
        if (status && item.status !== status) return false
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
    url: '/equipment',
    type: 'post',
    response: config => {
      const newEquipment = {
        id: Mock.mock('@increment(1)'),
        ...config.body,
        createTime: Mock.mock('@datetime'),
        updateTime: Mock.mock('@datetime')
      }
      equipmentList.push(newEquipment)
      return {
        code: 20000,
        data: '添加成功'
      }
    }
  },
  {
    url: '/equipment/detail',
    type: 'get',
    response: config => {
      console.log('Detail request received:', config)
      console.log('Config type:', typeof config)
      console.log('Config keys:', Object.keys(config))
      console.log('Config url:', config.url)
      console.log('Config originalUrl:', config.originalUrl)
      console.log('Config params:', config.params)
      console.log('Config query:', config.query)
      console.log('Config body:', config.body)
      
      try {
        // 尝试从不同的属性中获取 URL
        const urlToUse = config.url || config.originalUrl || ''
        console.log('URL to use:', urlToUse)
        
        // 尝试从 URL 中提取 ID
        const matches = urlToUse.match(/\/equipment\/detail\/(\d+)/)
        console.log('URL matches:', matches)
        
        if (!matches) {
          console.log('No ID found in URL')
          return {
            code: 20000,
            data: null
          }
        }
        
        const id = parseInt(matches[1])
        console.log('Extracted ID:', id)
        
        const equipment = equipmentList.find(item => item.id === id)
        console.log('Found equipment:', equipment)
        
        return {
          code: 20000,
          data: equipment || null
        }
      } catch (error) {
        console.error('Error in detail response:', error)
        return {
          code: 50000,
          message: error.message
        }
      }
    }
  },
  {
    url: '/equipment/update',
    type: 'put',
    response: config => {
      const id = parseInt(config.url.replace(/.*\/equipment\/update\//, ''))
      const index = equipmentList.findIndex(item => item.id === id)
      if (index > -1) {
        equipmentList[index] = {
          ...equipmentList[index],
          ...config.body,
          updateTime: Mock.Random.datetime()
        }
      }
      return {
        code: 20000,
        data: '更新成功'
      }
    }
  },
  {
    url: '/equipment/delete',
    type: 'delete',
    response: config => {
      const id = parseInt(config.url.replace(/.*\/equipment\/delete\//, ''))
      const index = equipmentList.findIndex(item => item.id === id)
      if (index > -1) {
        equipmentList.splice(index, 1)
      }
      return {
        code: 20000,
        data: '删除成功'
      }
    }
  },
  {
    url: '/equipment/room-options',
    type: 'get',
    response: () => {
      return {
        code: 20000,
        data: roomList
      }
    }
  },
  {
    url: '/equipment/manager-options',
    type: 'get',
    response: () => {
      return {
        code: 20000,
        data: managerList
      }
    }
  },
  // 获取设备申报审核列表
  {
    url: '/equipment/approval/list',
    type: 'get',
    response: config => {
      const { keyword, status, page = 1, limit = 10 } = config.query

      let mockList = approvalList.filter(item => {
        if (keyword && !item.equipmentName.includes(keyword) && !item.applicant.includes(keyword)) return false
        if (status && item.status !== status) return false
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
  // 审核通过设备申请
  {
    url: '/equipment/approval/approve/\\d+',
    type: 'post',
    response: config => {
      const id = parseInt(config.url.match(/\/approve\/(\d+)/)[1])
      const index = approvalList.findIndex(item => item.id === id)
      if (index > -1) {
        approvalList[index].status = 'approved'
        approvalList[index].updateTime = Mock.Random.datetime()
      }
      return {
        code: 20000,
        data: '审核通过成功'
      }
    }
  },
  // 拒绝设备申请
  {
    url: '/equipment/approval/reject/\\d+',
    type: 'post',
    response: config => {
      const id = parseInt(config.url.match(/\/reject\/(\d+)/)[1])
      const index = approvalList.findIndex(item => item.id === id)
      if (index > -1) {
        approvalList[index].status = 'rejected'
        approvalList[index].rejectReason = config.body.reason
        approvalList[index].updateTime = Mock.Random.datetime()
      }
      return {
        code: 20000,
        data: '已拒绝申请'
      }
    }
  },
  // 批量审核通过
  {
    url: '/equipment/approval/batch-approve',
    type: 'post',
    response: config => {
      const { ids } = config.body
      ids.forEach(id => {
        const index = approvalList.findIndex(item => item.id === id)
        if (index > -1) {
          approvalList[index].status = 'approved'
          approvalList[index].updateTime = Mock.Random.datetime()
        }
      })
      return {
        code: 20000,
        data: '批量审核通过成功'
      }
    }
  },
  // 获取设备申报详情
  {
    url: '/equipment/approval/detail/\\d+',
    type: 'get',
    response: config => {
      const id = parseInt(config.url.match(/\/detail\/(\d+)/)[1])
      const item = approvalList.find(item => item.id === id)
      return {
        code: 20000,
        data: item || null
      }
    }
  }
] 