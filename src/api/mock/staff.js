import Mock from 'mockjs'

// 生成随机数据
const staffList = Mock.mock({
  'rows|30': [{
    'id|+1': 1,
    'employeeId': function() {
      return 'EMP' + Mock.Random.string('number', 6)
    },
    'name': '@cname',
    'gender|1': [1, 2],
    'departmentId': function() {
      return Mock.Random.pick([1, 2, 3, 4, 5])
    },
    'departmentName': function() {
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
    'entryDate': '@date',
    'status|1': [1, 0],
    'phone': /^1[3-9]\d{9}$/,
    'email': '@email',
    'address': '@county(true)'
  }],
  'total': 30
})

// 部门树形数据
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

// 职位列表
const positionList = [
  { value: '教授', label: '教授' },
  { value: '副教授', label: '副教授' },
  { value: '讲师', label: '讲师' },
  { value: '助教', label: '助教' }
]

// 职称列表
const titleList = [
  { value: '高级', label: '高级' },
  { value: '中级', label: '中级' },
  { value: '初级', label: '初级' }
]

// 模拟接口
Mock.mock(/\/api\/staff\/list/, 'get', (options) => {
  const { url } = options
  const params = new URLSearchParams(url.split('?')[1])
  const pageNum = parseInt(params.get('pageNum')) || 1
  const pageSize = parseInt(params.get('pageSize')) || 10
  const name = params.get('name')
  const employeeId = params.get('employeeId')

  let filteredList = staffList.rows

  // 按条件筛选
  if (name) {
    filteredList = filteredList.filter(item => item.name.includes(name))
  }
  if (employeeId) {
    filteredList = filteredList.filter(item => item.employeeId.includes(employeeId))
  }

  // 分页
  const start = (pageNum - 1) * pageSize
  const end = start + pageSize
  const rows = filteredList.slice(start, end)

  return {
    code: 200,
    msg: 'success',
    data: {
      rows,
      total: filteredList.length
    }
  }
})

// 获取部门树
Mock.mock('/api/department/tree', 'get', {
  code: 200,
  msg: 'success',
  data: departmentTree
})

// 获取职位列表
Mock.mock('/api/position/list', 'get', {
  code: 200,
  msg: 'success',
  data: positionList
})

// 获取职称列表
Mock.mock('/api/title/list', 'get', {
  code: 200,
  msg: 'success',
  data: titleList
})

// 新增员工
Mock.mock('/api/staff', 'post', (options) => {
  const body = JSON.parse(options.body)
  return {
    code: 200,
    msg: 'success',
    data: {
      ...body,
      id: Mock.Random.increment()
    }
  }
})

// 修改员工
Mock.mock('/api/staff', 'put', {
  code: 200,
  msg: 'success'
})

// 删除员工
Mock.mock(/\/api\/staff\/\d+/, 'delete', {
  code: 200,
  msg: 'success'
})

// 批量删除
Mock.mock('/api/staff/batch', 'delete', {
  code: 200,
  msg: 'success'
})
