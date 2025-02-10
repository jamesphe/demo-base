const Mock = require('mockjs')

// 用于生成ID的计数器
let idCounter = 100

// 深度克隆函数
const cloneDeep = (obj) => JSON.parse(JSON.stringify(obj))

// 初始部门列表
const departmentList = [
  {
    id: 1,
    name: '党政办公室',
    code: 'DZB',
    parentId: 0,
    leader: '张明',
    phone: '13800138001',
    orderNum: 1,
    createTime: '2023-01-01'
  },
  {
    id: 2,
    name: '组织人事处',
    code: 'ZZB',
    parentId: 0,
    leader: '李红',
    phone: '13800138002',
    orderNum: 2,
    createTime: '2023-01-01'
  },
  {
    id: 3,
    name: '教务处',
    code: 'JWC',
    parentId: 0,
    leader: '王强',
    phone: '13800138003',
    orderNum: 3,
    createTime: '2023-01-01'
  },
  {
    id: 4,
    name: '学生处',
    code: 'XSC',
    parentId: 0,
    leader: '赵阳',
    phone: '13800138004',
    orderNum: 4,
    createTime: '2023-01-01'
  },
  {
    id: 5,
    name: '科研处',
    code: 'KYC',
    parentId: 0,
    leader: '钱伟',
    phone: '13800138005',
    orderNum: 5,
    createTime: '2023-01-01'
  },
  {
    id: 6,
    name: '财务处',
    code: 'CWC',
    parentId: 0,
    leader: '孙波',
    phone: '13800138006',
    orderNum: 6,
    createTime: '2023-01-01'
  },
  {
    id: 7,
    name: '信息工程系',
    code: 'XXX',
    parentId: 0,
    leader: '周杰',
    phone: '13800138007',
    orderNum: 7,
    createTime: '2023-01-01',
    children: [
      {
        id: 71,
        name: '软件技术教研室',
        code: 'RJ',
        parentId: 7,
        leader: '吴敏',
        phone: '13800138071',
        orderNum: 1,
        createTime: '2023-01-01'
      },
      {
        id: 72,
        name: '计算机网络教研室',
        code: 'JW',
        parentId: 7,
        leader: '郑华',
        phone: '13800138072',
        orderNum: 2,
        createTime: '2023-01-01'
      },
      {
        id: 73,
        name: '数字媒体教研室',
        code: 'SM',
        parentId: 7,
        leader: '冯雪',
        phone: '13800138073',
        orderNum: 3,
        createTime: '2023-01-01'
      }
    ]
  },
  {
    id: 8,
    name: '机械工程系',
    code: 'JXX',
    parentId: 0,
    leader: '陈亮',
    phone: '13800138008',
    orderNum: 8,
    createTime: '2023-01-01',
    children: [
      {
        id: 81,
        name: '机械制造教研室',
        code: 'JZ',
        parentId: 8,
        leader: '杨光',
        phone: '13800138081',
        orderNum: 1,
        createTime: '2023-01-01'
      },
      {
        id: 82,
        name: '模具设计教研室',
        code: 'MJ',
        parentId: 8,
        leader: '黄海',
        phone: '13800138082',
        orderNum: 2,
        createTime: '2023-01-01'
      },
      {
        id: 83,
        name: '数控技术教研室',
        code: 'SK',
        parentId: 8,
        leader: '胡明',
        phone: '13800138083',
        orderNum: 3,
        createTime: '2023-01-01'
      }
    ]
  },
  {
    id: 9,
    name: '经济管理系',
    code: 'JJX',
    parentId: 0,
    leader: '朱婷',
    phone: '13800138009',
    orderNum: 9,
    createTime: '2023-01-01',
    children: [
      {
        id: 91,
        name: '会计教研室',
        code: 'KJ',
        parentId: 9,
        leader: '汪洋',
        phone: '13800138091',
        orderNum: 1,
        createTime: '2023-01-01'
      },
      {
        id: 92,
        name: '市场营销教研室',
        code: 'SC',
        parentId: 9,
        leader: '韩雪',
        phone: '13800138092',
        orderNum: 2,
        createTime: '2023-01-01'
      },
      {
        id: 93,
        name: '物流管理教研室',
        code: 'WL',
        parentId: 9,
        leader: '魏明',
        phone: '13800138093',
        orderNum: 3,
        createTime: '2023-01-01'
      }
    ]
  },
  {
    id: 10,
    name: '基础教学部',
    code: 'JCB',
    parentId: 0,
    leader: '董强',
    phone: '13800138010',
    orderNum: 10,
    createTime: '2023-01-01',
    children: [
      {
        id: 101,
        name: '公共英语教研室',
        code: 'GY',
        parentId: 10,
        leader: '范文',
        phone: '13800138101',
        orderNum: 1,
        createTime: '2023-01-01'
      },
      {
        id: 102,
        name: '高等数学教研室',
        code: 'GS',
        parentId: 10,
        leader: '唐华',
        phone: '13800138102',
        orderNum: 2,
        createTime: '2023-01-01'
      },
      {
        id: 103,
        name: '思政教研室',
        code: 'SZ',
        parentId: 10,
        leader: '徐梅',
        phone: '13800138103',
        orderNum: 3,
        createTime: '2023-01-01'
      }
    ]
  }
]

// 查找部门函数
const findDepartment = (list, id) => {
  for (const item of list) {
    if (item.id === id) {
      return item
    }
    if (item.children) {
      const found = findDepartment(item.children, id)
      if (found) return found
    }
  }
  return null
}

// 删除部门函数
const deleteDepartment = (list, id) => {
  for (let i = 0; i < list.length; i++) {
    if (list[i].id === id) {
      list.splice(i, 1)
      return true
    }
    if (list[i].children) {
      if (deleteDepartment(list[i].children, id)) {
        if (list[i].children.length === 0) {
          delete list[i].children
        }
        return true
      }
    }
  }
  return false
}

module.exports = [
  // 获取部门列表
  {
    url: '/vue-element-admin/department/list',
    type: 'get',
    response: _ => {
      return {
        code: 20000,
        data: cloneDeep(departmentList)
      }
    }
  },

  // 新增部门
  {
    url: '/vue-element-admin/department',
    type: 'post',
    response: config => {
      const { parentId, name, code, leader, phone, orderNum } = config.body
      const newDept = {
        id: ++idCounter,
        name,
        code,
        parentId,
        leader,
        phone,
        orderNum,
        createTime: Mock.mock('@date')
      }

      if (parentId === 0) {
        departmentList.push(newDept)
      } else {
        const parent = findDepartment(departmentList, parentId)
        if (parent) {
          if (!parent.children) {
            parent.children = []
          }
          parent.children.push(newDept)
        }
      }

      return {
        code: 20000,
        data: 'success'
      }
    }
  },

  // 修改部门
  {
    url: '/vue-element-admin/department',
    type: 'put',
    response: config => {
      const { id, parentId, name, code, leader, phone, orderNum } = config.body
      const dept = findDepartment(departmentList, id)
      if (dept) {
        dept.name = name
        dept.code = code
        dept.parentId = parentId
        dept.leader = leader
        dept.phone = phone
        dept.orderNum = orderNum
      }

      return {
        code: 20000,
        data: 'success'
      }
    }
  },

  // 删除部门
  {
    url: '/vue-element-admin/department/\\d+',
    type: 'delete',
    response: config => {
      const id = parseInt(config.url.match(/\/department\/(\d+)/)[1])
      deleteDepartment(departmentList, id)
      return {
        code: 20000,
        data: 'success'
      }
    }
  }
] 