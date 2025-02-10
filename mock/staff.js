const Mock = require('mockjs')

const staffList = Mock.mock({
  'items|30': [{
    id: '@increment',
    'employeeId': function() {
      return 'EMP' + Mock.Random.string('number', 6)
    },
    name: '@cname',
    'gender|1': [1, 2],
    'departmentId|1': [1, 2, 3, 4, 5],
    departmentName: function() {
      const depts = {
        1: '教务处',
        2: '人事处',
        3: '信息工程系',
        4: '机械工程系',
        5: '经济管理系'
      }
      return depts[this.departmentId]
    },
    'position|1': ['教授', '副教授', '讲师', '助教'],
    'title|1': ['高级', '中级', '初级'],
    'education|1': ['博士', '硕士', '本科', '专科'],
    entryDate: '@date',
    'status|1': [1, 0],
    'staffType|1': [1, 2, 3, 4, 5],
    phone: /^1[3-9]\d{9}$/,
    email: '@email',
    address: '@county(true)'
  }]
})

const departmentTree = [
  {
    id: 1,
    label: '教务处',
    value: 1
  },
  {
    id: 2,
    label: '人事处',
    value: 2
  },
  {
    id: 3,
    label: '信息工程系',
    value: 3,
    children: [
      {
        id: 31,
        label: '软件开发教研室',
        value: 31
      },
      {
        id: 32,
        label: '网络工程教研室',
        value: 32
      }
    ]
  },
  {
    id: 4,
    label: '机械工程系',
    value: 4
  },
  {
    id: 5,
    label: '经济管理系',
    value: 5
  }
]

const positionList = [
  { value: '教授', label: '教授' },
  { value: '副教授', label: '副教授' },
  { value: '讲师', label: '讲师' },
  { value: '助教', label: '助教' }
]

const titleList = [
  { value: '高级', label: '高级' },
  { value: '中级', label: '中级' },
  { value: '初级', label: '初级' }
]

const staffTypeList = [
  { value: 1, label: '事业编制在职' },
  { value: 2, label: '非事业编制管理岗' },
  { value: 3, label: '工勤岗' },
  { value: 4, label: '退休' },
  { value: 5, label: '离职' }
]

module.exports = [
  // 获取员工列表
  {
    url: '/vue-element-admin/staff/list',
    type: 'get',
    response: config => {
      const { name, employeeId, pageNum = 1, pageSize = 10 } = config.query

      let mockList = staffList.items
      if (name) {
        mockList = mockList.filter(item => item.name.includes(name))
      }
      if (employeeId) {
        mockList = mockList.filter(item => item.employeeId.includes(employeeId))
      }

      const pageList = mockList.filter((item, index) => index < pageSize * pageNum && index >= pageSize * (pageNum - 1))

      return {
        code: 20000,
        data: {
          total: mockList.length,
          items: pageList
        }
      }
    }
  },

  // 获取部门树
  {
    url: '/vue-element-admin/department/tree',
    type: 'get',
    response: _ => {
      return {
        code: 20000,
        data: departmentTree
      }
    }
  },

  // 获取职位列表
  {
    url: '/vue-element-admin/position/list',
    type: 'get',
    response: _ => {
      return {
        code: 20000,
        data: positionList
      }
    }
  },

  // 获取职称列表
  {
    url: '/vue-element-admin/title/list',
    type: 'get',
    response: _ => {
      return {
        code: 20000,
        data: titleList
      }
    }
  },

  // 获取教职工类型列表
  {
    url: '/vue-element-admin/staff/type/list',
    type: 'get',
    response: _ => {
      return {
        code: 20000,
        data: staffTypeList
      }
    }
  },

  // 新增员工
  {
    url: '/vue-element-admin/staff',
    type: 'post',
    response: {
      code: 20000,
      data: 'success'
    }
  },

  // 修改员工
  {
    url: '/vue-element-admin/staff',
    type: 'put',
    response: {
      code: 20000,
      data: 'success'
    }
  },

  // 删除员工
  {
    url: '/vue-element-admin/staff/[A-Za-z0-9]',
    type: 'delete',
    response: {
      code: 20000,
      data: 'success'
    }
  },

  // 批量删除
  {
    url: '/vue-element-admin/staff/batch',
    type: 'delete',
    response: {
      code: 20000,
      data: 'success'
    }
  }
] 