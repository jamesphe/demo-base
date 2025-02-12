import Mock from 'mockjs'

const List = []
const count = 20

// 耗材类型列表
const consumableTypes = ['办公用品', '实验耗材', '教学用品', '清洁用品', '电子耗材']

// 用途列表
const purposeList = [
  '日常教学使用',
  '实验课程使用',
  '学生实训项目',
  '办公室日常使用',
  '实训室维护使用',
  '教师教学演示',
  '学生课后练习',
  '设备日常维护'
]

// 申请人列表
const applicants = ['张老师', '李老师', '王老师', '赵老师', '刘老师']

// 生成模拟数据
for (let i = 0; i < count; i++) {
  List.push(Mock.mock({
    id: '@increment',
    applicant: '@pick(' + JSON.stringify(applicants) + ')',
    'status|1': ['pending', 'approved', 'rejected'],
    name: '@pick(' + JSON.stringify([
      '打印纸', 'A4纸', '记号笔', '白板笔', '实验手套',
      '清洁剂', '电烙铁头', '焊锡丝', '元器件', '电子元件',
      'PCB板', '导线', '螺丝刀', '镊子', '万用表笔'
    ]) + ')',
    'type|1': consumableTypes,
    quantity: '@integer(1, 100)',
    unit: '@pick(["个", "包", "盒", "卷", "套"])',
    purpose: '@pick(' + JSON.stringify(purposeList) + ')',
    applyDate: '@datetime("yyyy-MM-dd HH:mm:ss")',
    approver: '@cname',
    approveDate: '@datetime("yyyy-MM-dd HH:mm:ss")',
    remark: '@cparagraph(1, 3)',
    department: '@pick(["电子工程系", "机械工程系", "计算机系", "自动化系"])',
    urgency: '@pick(["普通", "紧急", "特急"])',
    expectedDate: '@date("yyyy-MM-dd")',
    cost: '@float(10, 1000, 2, 2)',
    supplier: '@company',
    contact: '@name',
    phone: /1[3-9]\d{9}/,
    'attachments|0-3': ['@image("200x200", "@color", "@word")']
  }))
}

export default [
  {
    url: '/consumable/apply/list.*',
    type: 'get',
    response: config => {
      const { page = 1, limit = 10, status, type, applicant, dateRange, sort, order } = config.query
      console.log('Mock received query:', config.query)

      let mockList = List.filter(item => {
        // 状态筛选
        if (status && item.status !== status) return false
        // 类型筛选
        if (type && item.type !== type) return false
        // 申请人筛选
        if (applicant && !item.applicant.includes(applicant)) return false
        // 日期范围筛选
        if (dateRange && dateRange.length === 2) {
          const start = new Date(dateRange[0]).getTime()
          const end = new Date(dateRange[1]).getTime()
          const curr = new Date(item.applyDate).getTime()
          if (curr < start || curr > end) return false
        }
        return true
      })

      // 添加排序逻辑
      if (sort && order) {
        console.log('Sorting by:', sort, 'order:', order)
        const isAsc = order === 'asc'
        mockList.sort((a, b) => {
          let compareA = a[sort]
          let compareB = b[sort]
          console.log('Comparing:', compareA, compareB)

          // 日期类型特殊处理
          if (sort === 'applyDate') {
            compareA = new Date(compareA).getTime()
            compareB = new Date(compareB).getTime()
          }

          // 紧急程度特殊处理
          if (sort === 'urgency') {
            const urgencyOrder = { '特急': 3, '紧急': 2, '普通': 1 }
            compareA = urgencyOrder[compareA]
            compareB = urgencyOrder[compareB]
          }

          console.log('After processing:', compareA, compareB)
          if (compareA < compareB) return isAsc ? -1 : 1
          if (compareA > compareB) return isAsc ? 1 : -1
          return 0
        })
        console.log('Sorted list:', mockList)
      }

      const pageList = mockList.filter((item, index) => index < limit * page && index >= limit * (page - 1))
      console.log('Final page list:', pageList)

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
    url: '/consumable/apply/create',
    type: 'post',
    response: config => {
      const { name, quantity, purpose } = config.body
      List.unshift(Mock.mock({
        id: '@increment',
        name,
        quantity,
        purpose,
        applicant: '@cname',
        status: 'pending',
        applyDate: '@now',
        type: '@pick(' + JSON.stringify(consumableTypes) + ')',
        department: '@pick(["电子工程系", "机械工程系", "计算机系", "自动化系"])'
      }))
      return {
        code: 20000,
        data: 'success'
      }
    }
  },
  {
    url: '/consumable/apply/\\d+/status',
    type: 'put',
    response: config => {
      const { status } = config.body
      const id = config.url.split('/').pop()
      const item = List.find(item => item.id === parseInt(id))
      if (item) {
        item.status = status
        item.approver = Mock.mock('@cname')
        item.approveDate = Mock.mock('@now')
      }
      return {
        code: 20000,
        data: 'success'
      }
    }
  },
  {
    // 获取耗材类型列表
    url: '/consumable/types',
    type: 'get',
    response: _ => {
      return {
        code: 20000,
        data: consumableTypes
      }
    }
  },
  {
    // 获取申请详情
    url: '/consumable/apply/detail/\\d+',
    type: 'get',
    response: config => {
      const id = parseInt(config.url.split('/').pop())
      const item = List.find(item => item.id === id)
      return {
        code: 20000,
        data: item
      }
    }
  }
] 