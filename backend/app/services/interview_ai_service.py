from typing import Dict, Any, List, AsyncGenerator
from sqlalchemy.orm import Session
from fastapi import HTTPException
import logging

from app.services.resume_service import resume_service
from app.services.job_service import job_service
from app.services.llm_service import llm_service
from app.schemas.interview import InterviewGuideRequest

logger = logging.getLogger(__name__)


class InterviewAIService:
    def _format_skills(self, skills: List[Dict]) -> str:
        """格式化技能列表
        
        Args:
            skills: 技能列表，每个技能是一个字典，包含name和level等信息
            
        Returns:
            格式化后的技能字符串，例如：'Python(熟练)、Java(精通)、Go(了解)'
        """
        if not skills:
            return "未提供技能信息"
        
        try:
            formatted_skills = []
            for skill in skills:
                if isinstance(skill, dict):
                    # 如果是字典格式，尝试获取name和level
                    name = skill.get('name', '')
                    level = skill.get('level', '')
                    if name and level:
                        formatted_skills.append(f"{name}({level})")
                    elif name:
                        formatted_skills.append(name)
                elif isinstance(skill, str):
                    # 如果是字符串格式，直接使用
                    formatted_skills.append(skill)
                
            return "、".join(formatted_skills) if formatted_skills else \
                   "未提供技能信息"
            
        except Exception as e:
            logger.error(f"格式化技能信息失败: {str(e)}")
            return "技能信息格式化失败"

    def _format_work_experience(self, work_experience: List[Dict]) -> str:
        """格式化工作经验"""
        if not work_experience:
            return "未提供工作经验"
        
        formatted = []
        for exp in work_experience:
            exp_str = (
                f"- {exp.get('company', '未知公司')} | "
                f"{exp.get('position', '未知职位')}\n"
            )
            exp_str += (
                f"  时间：{exp.get('start_date', '')} 至 "
                f"{exp.get('end_date', '')}\n"
            )
            if exp.get('description'):
                exp_str += f"  描述：{exp.get('description')}\n"
            formatted.append(exp_str)
        
        return "\n".join(formatted)

    def _format_education(self, education: List[Dict]) -> str:
        """格式化教育经历"""
        if not education:
            return "未提供教育经历"
        
        formatted = []
        for edu in education:
            edu_str = (
                f"- {edu.get('school', '未知学校')} | "
                f"{edu.get('major', '未知专业')} | "
                f"{edu.get('degree', '未知学位')}"
            )
            formatted.append(edu_str)
        
        return "\n".join(formatted)

    def _format_job_requirements(self, requirements: Dict) -> str:
        """格式化职位要求"""
        if not requirements:
            return "未提供职位要求"
        
        formatted = []
        if requirements.get('experience'):
            formatted.append(f"工作经验：{requirements['experience']}")
        if requirements.get('education'):
            formatted.append(f"学历要求：{requirements['education']}")
        if requirements.get('skills'):
            formatted.append(f"技能要求：{', '.join(requirements['skills'])}")
        if requirements.get('description'):
            formatted.append(f"职位描述：{requirements['description']}")
        
        return "\n".join(formatted)

    def _get_industry_specific_prompt(self, industry: str, role: str) -> str:
        """根据行业和角色获取特定的提示词增强部分
        
        Args:
            industry: 行业名称，如'信息技术'、'金融'等
            role: 面试官角色，如'技术面试官'、'部门负责人'等
            
        Returns:
            行业和角色特定的提示词部分
        """
        # 根据行业生成特定的提示增强
        industry_prompts = {
            "信息技术": {
                "技术面试官": """
此次面试针对信息技术行业，你应特别关注：
1. 候选人的编码实践和系统设计能力
2. 算法理解和问题解决思路
3. 新技术学习能力和技术视野
4. 代码质量和工程实践经验
5. 云服务和分布式系统知识掌握程度
                
设计面试问题时，应包含IT行业特定的技术考察点，如DevOps实践、微服务架构、云原生应用等话题。
""",
                "部门负责人": """
此次面试针对信息技术行业，你应特别关注：
1. 候选人的技术管理经验和跨团队协作能力
2. 技术决策和架构规划能力
3. 敏捷/项目管理方法论应用经验
4. 对技术趋势的把握程度
5. IT团队的管理和激励经验
                
设计面试问题时，应包含IT行业特定的管理考察点，如技术团队建设、跨部门协作机制、技术债务管理等话题。
""",
                "人事面试官": """
此次面试针对信息技术行业，你应特别关注：
1. IT人才市场动态和薪资水平了解
2. 技术人才成长路径和职业规划理解
3. 加班文化接受度和工作节奏适应性
4. 远程工作和弹性工作制度接受度
                
设计面试问题时，应包含IT行业特定的HR考察点，如技术团队文化建设、技术人才保留策略、工程师职业发展通道等话题。
""",
                "业务面试官": """
此次面试针对信息技术行业，你应特别关注：
1. 产品生命周期和业务模式理解
2. 用户需求分析和产品定位能力
3. IT解决方案的商业价值判断能力
4. 数字化转型和创新模式认知
                
设计面试问题时，应包含IT行业特定的业务考察点，如产品市场匹配度、用户体验设计、数据驱动决策等话题。
"""
            },
            "金融": {
                "技术面试官": """
此次面试针对金融行业，你应特别关注：
1. 金融领域技术应用知识和经验
2. 金融数据处理和分析能力
3. 风控系统和反欺诈技术经验
4. 支付系统和交易处理技术理解
5. 金融数据安全和隐私保护意识
                
设计面试问题时，应包含金融行业特定的技术考察点，如高并发交易系统、合规监管技术实现、金融级容灾方案等话题。
""",
                "部门负责人": """
此次面试针对金融行业，你应特别关注：
1. 金融业务流程和产品知识理解
2. 业务与技术衔接能力
3. 金融行业发展趋势把握
4. 金融监管政策理解和执行经验
5. 风险管理体系构建经验
                
设计面试问题时，应包含金融行业特定的管理考察点，如合规文化建设、风险控制流程、金融安全管理等话题。
""",
                "人事面试官": """
此次面试针对金融行业，你应特别关注：
1. 金融行业从业资格和专业资质
2. 职业操守和道德准则认知
3. 对金融行业工作强度的适应能力
4. 稳定性和保密意识
                
设计面试问题时，应包含金融行业特定的HR考察点，如职业道德评估、压力承受能力、保密意识培养等话题。
""",
                "业务面试官": """
此次面试针对金融行业，你应特别关注：
1. 金融产品和服务理解深度
2. 金融业务流程和规则认知
3. 风险评估和控制意识
4. 金融监管政策理解和应用能力
                
设计面试问题时，应包含金融行业特定的业务考察点，如金融市场分析、风险与收益平衡、合规业务发展等话题。
"""
            },
            "医疗健康": {
                "技术面试官": """
此次面试针对医疗健康行业，你应特别关注：
1. 医疗数据标准和互操作性理解
2. 临床信息系统开发经验
3. 医疗数据安全和隐私保护意识
4. 医疗影像处理和AI应用能力
                
设计面试问题时，应包含医疗行业特定的技术考察点，如医疗数据合规处理、患者隐私保护、医疗软件验证流程等话题。
""",
                "部门负责人": """
此次面试针对医疗健康行业，你应特别关注：
1. 医疗质量管理和患者安全意识
2. 跨专业团队管理能力
3. 医疗行业合规和认证经验
4. 医疗服务改进思路
                
设计面试问题时，应包含医疗行业特定的管理考察点，如医疗质量控制、患者满意度提升、医疗团队协作等话题。
""",
                "业务面试官": """
此次面试针对医疗健康行业，你应特别关注：
1. 医疗服务流程和专业术语理解
2. 医疗产品和解决方案知识
3. 医患关系管理和服务意识
4. 医疗质量管理和风险控制能力
                
设计面试问题时，应包含医疗行业特定的业务考察点，如医疗资源配置、医疗服务价值分析、医疗伦理决策等话题。
"""
            },
            "制造业": {
                "技术面试官": """
此次面试针对制造业，你应特别关注：
1. 制造工艺和质量控制知识
2. 工业自动化和智能制造认知
3. 生产系统优化和效率提升经验
4. 对材料科学和工程标准的理解
                
设计面试问题时，应包含制造业特定的技术考察点，如工业物联网应用、生产线自动化、质量控制系统等话题。
""",
                "部门负责人": """
此次面试针对制造业，你应特别关注：
1. 生产管理和供应链优化经验
2. 质量控制体系和精益生产理念
3. 资源调配和产能规划能力
4. 对安全生产和环保要求的重视
                
设计面试问题时，应包含制造业特定的管理考察点，如精益生产实践、供应链风险管理、产能规划决策等话题。
""",
                "业务面试官": """
此次面试针对制造业，你应特别关注：
1. 制造流程和产业链理解深度
2. 产品质量标准和控制方法认知
3. 生产计划和库存管理能力
4. 供应链管理和采购策略理解
                
设计面试问题时，应包含制造业特定的业务考察点，如制造成本分析、产能规划策略、产品生命周期管理等话题。
"""
            }
        }
        
        # 获取默认提示信息
        default_prompt = """
请根据候选人的具体行业背景和应聘职位，特别关注：
1. 行业专业知识和术语理解
2. 行业特定技能和实践经验
3. 行业趋势把握和发展方向认知
4. 行业法规和标准熟悉程度

设计面试问题时，应包含行业特定的考察点，确保问题能有效评估候选人的行业适应性和专业深度。
"""
        
        # 如果有匹配的行业和角色提示，则返回，否则返回默认提示
        if industry in industry_prompts and role in industry_prompts[industry]:
            return industry_prompts[industry][role]
        else:
            return default_prompt

    def _extract_key_job_info(self, job) -> str:
        """提取职位关键信息用于生成自适应结构
        
        Args:
            job: 职位对象
            
        Returns:
            提取的关键信息文本
        """
        job_info = []
        
        if hasattr(job, 'title') and job.title:
            job_info.append(f"职位名称: {job.title}")
        
        if hasattr(job, 'department') and job.department:
            job_info.append(f"部门: {job.department}")
        
        if hasattr(job, 'requirements') and job.requirements:
            if 'description' in job.requirements and job.requirements['description']:
                job_info.append(f"职位描述: {job.requirements['description']}")
            
            if ('responsibilities' in job.requirements and 
                    job.requirements['responsibilities']):
                resp_text = "职责: " + ", ".join(job.requirements['responsibilities'])
                job_info.append(resp_text)
            
            if 'skills' in job.requirements and job.requirements['skills']:
                skills_text = "技能要求: " + ", ".join(job.requirements['skills'])
                job_info.append(skills_text)
            
            if 'experience' in job.requirements and job.requirements['experience']:
                job_info.append(f"经验要求: {job.requirements['experience']}")
        
        return "\n".join(job_info)

    def _extract_key_resume_info(self, resume) -> str:
        """提取简历关键信息用于生成自适应结构
        
        Args:
            resume: 简历对象
            
        Returns:
            提取的关键信息文本
        """
        resume_info = []
        
        if hasattr(resume, 'name') and resume.name:
            resume_info.append(f"姓名: {resume.name}")
        
        if hasattr(resume, 'current_position') and resume.current_position:
            resume_info.append(f"当前职位: {resume.current_position}")
            
        if hasattr(resume, 'experience_years') and resume.experience_years:
            resume_info.append(f"工作年限: {resume.experience_years}年")
        
        if hasattr(resume, 'highest_education') and resume.highest_education:
            resume_info.append(f"最高学历: {resume.highest_education}")
        
        if hasattr(resume, 'major') and resume.major:
            resume_info.append(f"专业: {resume.major}")
        
        # 技能信息
        if hasattr(resume, 'skills') and resume.skills:
            skills_text = self._format_skills(resume.skills)
            resume_info.append(f"技能: {skills_text}")
        
        # 简要工作经历
        if hasattr(resume, 'work_experience') and resume.work_experience:
            work_exp = []
            for exp in resume.work_experience[:2]:  # 只取最近两段经历
                company = exp.get('company', '未知公司')
                position = exp.get('position', '未知职位')
                work_exp.append(f"{company} - {position}")
            
            if work_exp:
                resume_info.append(f"工作经历: {'; '.join(work_exp)}")
        
        return "\n".join(resume_info)

    async def get_adaptive_structure(
            self, db: Session, resume, job, role: str, 
            industry: str = None) -> str:
        """使用LLM根据候选人和职位信息智能生成最合适的文档结构
        
        Args:
            db: 数据库会话
            resume: 简历对象
            job: 职位对象
            role: 面试官角色
            industry: 行业，可选
            
        Returns:
            生成的自适应文档结构
        """
        # 提取简历和职位关键信息
        resume_info = self._extract_key_resume_info(resume)
        job_info = self._extract_key_job_info(job)
        
        # 构建结构生成提示
        industry_context = f"行业背景: {industry}" if industry else ""
        structure_prompt = f"""
分析以下简历和职位信息，为{role}生成最合适的面试指导文档结构：

候选人信息:
{resume_info}

应聘职位信息:
{job_info}

{industry_context}

你需要考虑候选人背景和职位要求的匹配度，以及{role}在面试中的特定关注点。
请设计一个完整的面试指导文档结构，包括但不限于以下部分:
1. 候选人评估部分
2. 核心能力考察要点
3. 经验验证部分
4. 面试问题建议(分类别)
5. 评估标准

请直接返回Markdown格式的文档结构，包括清晰的章节和子项。不要包含具体内容，只提供结构框架。"""

        try:
            # 获取LLM配置并使用它
            llm_config = await llm_service.get_default_config(db)
            
            # 构建系统提示
            system_prompt = """你是一位专业的面试指导专家。请根据提供的候选人信息和职位要求，
生成一份详细且高度针对性的面试指导文档。

你的文档必须包含以下组成部分：
1. 候选人与职位匹配度分析：详细分析候选人的技能、经验与职位要求的匹配情况
2. 核心能力评估框架：根据职位要求设计评估维度和标准
3. 分类面试问题：根据评估维度设计针对性问题
4. 每个问题的参考答案：基于候选人背景提供期望回答要点
5. 评分标准：为每个评估维度提供明确的评分指导

所有问题和评估维度必须高度个性化，直接针对候选人的具体背景和职位要求。
避免泛泛而谈或通用模板式的问题。
"""

            # 调用LLM生成自适应结构
            response = await llm_service.generate_completion(
                prompt=structure_prompt,
                system_prompt=system_prompt,
                db=db,
                max_tokens=1200,  # 允许生成足够详细的结构
                llm_config=llm_config  # 使用获取的配置
            )
            
            return response["content"]
        except Exception as e:
            logger.error(f"生成自适应文档结构失败: {str(e)}", exc_info=True)
            
            # 出错时返回默认结构
            return self._get_default_structure_for_role(role)
    
    def _get_default_structure_for_role(self, role: str) -> str:
        """获取角色的默认文档结构，用作备份
        
        Args:
            role: 面试官角色
            
        Returns:
            默认的文档结构
        """
        role_specific_content = {
            "部门负责人": """# 面试指导文档

## 一、候选人综合评估
- 领导潜力评估
- 管理经验分析
- 技术视野评价
- 职业发展契合度

## 二、管理能力考察要点
- 团队管理经验
- 资源调配能力
- 项目全局把控能力
- 危机处理能力

## 三、技术决策考察
- 技术选型思路
- 架构规划能力
- 技术风险评估
- 技术团队建设

## 四、沟通协作能力
- 跨部门协作经验
- 向上沟通能力
- 团队激励方式
- 冲突处理方法

## 五、面试问题建议
- 管理经验问题（3-4个）
- 团队建设问题（3-4个）
- 技术战略问题（3-4个）
- 领导力问题（3-4个）

## 六、评估参考标准
- 领导力评分标准
- 管理能力评分标准
- 战略思维评分标准
- 综合评价建议""",

            "技术面试官": """# 面试指导文档

## 一、候选人技术背景分析
- 技术栈匹配度分析
- 核心技能深度评估
- 技术广度评价
- 专业成长轨迹

## 二、技术能力考察要点
- 核心技术原理理解
- 算法与数据结构掌握
- 系统设计能力
- 代码质量与风格

## 三、项目经验考察
- 技术难点解决经验
- 架构设计思路
- 性能优化经验
- 技术选型判断

## 四、工程实践能力
- 测试与质量保障
- 开发流程与规范
- 问题诊断与调试
- 技术文档能力

## 五、面试问题建议
- 基础技术问题（3-4个）
- 项目实战问题（3-4个）
- 系统设计问题（3-4个）
- 编程实现问题（3-4个）

## 六、技术评估标准
- 技术基础评分标准
- 工程能力评分标准
- 架构思维评分标准
- 综合技术评价""",

            "人事面试官": """# 面试指导文档

## 一、候选人背景综述
- 职业经历连贯性
- 跳槽频率与原因
- 价值观与企业文化契合
- 职业发展意向评估

## 二、软技能评估要点
- 沟通表达能力
- 团队协作意识
- 压力应对方式
- 学习适应能力

## 三、职业素养考察
- 职业道德与价值观
- 工作责任感
- 时间管理能力
- 职业规划清晰度

## 四、发展潜力评估
- 学习能力与成长意愿
- 自我驱动力
- 创新思维
- 长期职业规划

## 五、面试问题建议
- 职业选择问题（3-4个）
- 情景应对问题（3-4个）
- 软技能考察问题（3-4个）
- 文化契合度问题（3-4个）

## 六、综合评估参考
- 软技能评分标准
- 文化契合度评分标准
- 发展潜力评分标准
- 整体录用建议""",

            "其他": """请根据面试官的具体角色，调整面试关注点和问题设计。

评估时，应全面分析候选人简历与职位要求的匹配度，找出需要重点考察的领域。

确保问题既能考察候选人的专业能力，又能满足特定角色的评估需求，
且所有问题都应直接针对候选人的具体情况和应聘职位制定。"""
        }
        
        default_structure = """# 面试指导文档

## 一、候选人背景分析
- 技能匹配度分析
- 经验匹配度分析
- 教育背景评估
- 职业发展轨迹分析

## 二、核心能力考察要点
- 专业能力评估
- 实践经验验证
- 问题解决能力
- 学习与适应能力

## 三、综合素质评估
- 沟通表达能力
- 团队协作能力
- 职业发展意愿
- 文化价值观契合

## 四、面试问题建议
- 专业能力问题（3-4个）
- 项目经验问题（3-4个）
- 情景应对问题（3-4个）
- 综合素质问题（3-4个）

## 五、评估标准与建议
- 专业能力评分标准
- 经验水平评分标准
- 综合素质评分标准
- 录用建议参考"""
        
        return role_specific_content.get(role, default_structure)

    def _get_role_prompt(self, role: str) -> str:
        """获取面试官角色的基本提示词
        
        Args:
            role: 面试官角色
            
        Returns:
            角色提示词
        """
        role_prompts = {
            "部门负责人": """作为部门负责人，你应严格关注以下方面，避免过度关注其他角色的职责范围：

1. 管理能力与领导潜力
   - 团队管理经验与方法论
   - 资源调配和项目规划能力
   - 战略思维和大局观
   - 决策能力和判断力

2. 业务理解与技术视野
   - 对业务需求的理解深度
   - 技术发展趋势的把握
   - 技术与业务的平衡能力
   - 风险评估能力

3. 人才发展与团队建设
   - 团队文化建设思路
   - 人才培养和梯队建设方法
   - 绩效管理和激励机制
   - 冲突处理能力

4. 跨部门协作与沟通
   - 与其他部门的协作经验
   - 向上管理和跨部门沟通能力
   - 项目推进和障碍排除能力
   - 共识达成能力

设计面试问题时，务必遵循以下原则：
- 必须以管理场景和领导决策为中心
- 使用情景化问题考察候选人的管理思路和领导风格
- 避免过于细节的技术实现问题，这是技术面试官的职责
- 不要涉及薪资期望、职业规划等人事话题，这是人事面试官的职责
- 重点关注候选人在团队管理、战略规划和决策方面的能力和经验

所有问题都应该能够帮助评估候选人是否能胜任管理岗位，而不是单纯的技术岗位或普通岗位。""",

            "技术面试官": """作为技术面试官，你应严格关注以下技术领域，避免过度关注其他角色的职责范围：

1. 技术深度与基础知识
   - 核心技术原理和底层机制的理解
   - 编程语言和框架的掌握程度
   - 算法和数据结构的应用能力
   - 系统设计和架构能力

2. 实践经验与问题解决
   - 技术难点攻克经历
   - 性能优化和故障排查经验
   - 技术选型和决策思路
   - 代码质量和工程实践

3. 技术学习与创新能力
   - 新技术学习和应用能力
   - 技术视野和知识广度
   - 技术探索和创新思维
   - 技术趋势判断能力

4. 技术协作与文档能力
   - 团队协作中的技术贡献
   - 技术文档和知识分享能力
   - 技术方案沟通表达能力
   - 代码审查和技术指导经验

设计面试问题时，务必遵循以下原则：
- 必须以技术场景和技术实现为中心
- 使用实际编程、设计或算法问题考察候选人的实操能力
- 避免管理决策和团队建设类问题，这是部门负责人的职责
- 不要涉及薪资期望、职业规划等人事话题，这是人事面试官的职责
- 重点关注候选人的技术思考方式和解决问题的思路过程

所有问题都应该能够帮助评估候选人的技术能力匹配度，而不是管理能力或文化适应性。""",

            "人事面试官": """作为人事面试官，你应严格关注以下软技能和文化适应性方面，绝对避免询问技术细节问题：

1. 职业发展与动机
   - 职业规划和发展目标
   - 加入公司的动机和预期
   - 价值观与公司文化契合度
   - 稳定性和忠诚度评估

2. 软技能与人际关系
   - 沟通表达能力
   - 团队协作意识和经验
   - 情商和人际关系处理能力
   - 压力应对和情绪管理能力

3. 自我认知与学习能力
   - 优势与不足的自我认知
   - 学习能力和适应性
   - 自我驱动和主动性
   - 时间管理和组织能力

4. 文化契合与职业素养
   - 工作习惯和职业态度
   - 责任感和诚信度
   - 创新思维和开放性
   - 多元化和包容性认知

设计面试问题时，务必遵循以下原则：
- 必须避免任何技术实现和专业技能的深度问题，这是技术面试官的职责
- 不要涉及团队管理和战略决策类问题，这是部门负责人的职责
- 应以行为面试法和情景假设为主要方法
- 重点关注候选人的软技能、文化适应性和发展潜力
- 适当关注薪资期望、入职时间等实际问题

所有问题都应该能够帮助评估候选人的文化契合度和职业发展匹配度，而不是技术能力。""",

            "业务面试官": """作为业务面试官，你应严格关注以下业务领域，避免过度关注其他角色的职责范围：

1. 业务理解与专业知识
   - 行业知识和业务理解深度
   - 业务流程和规则认知
   - 专业术语和标准掌握
   - 行业趋势和市场动态把握

2. 业务分析与决策能力
   - 业务问题分析能力
   - 数据解读和业务洞察能力
   - 业务风险评估能力
   - 业务决策和判断能力

3. 业务创新与价值创造
   - 业务优化和创新思维
   - 用户需求理解和分析能力
   - 商业价值评估能力
   - 解决方案设计能力

4. 业务协作与沟通能力
   - 跨职能团队协作经验
   - 业务需求表达和沟通能力
   - 业务推广和实施能力
   - 利益相关方管理经验

设计面试问题时，务必遵循以下原则：
- 必须以业务场景和业务决策为中心
- 使用案例分析和情景模拟考察候选人的业务思维
- 避免技术实现细节问题，这是技术面试官的职责
- 不要过度关注管理方法和团队建设，这是部门负责人的职责
- 不要涉及薪资期望、职业规划等人事话题，这是人事面试官的职责
- 重点关注候选人对业务的理解深度和业务决策能力

所有问题都应该能够帮助评估候选人的业务能力和专业素养，而不是技术能力或管理能力。"""
        }
        
        default_prompt = """请根据面试官的具体角色，严格区分不同角色的评估重点和问题范围：

1. 技术面试官：应专注于技术能力评估，包括编程能力、技术原理、系统设计等，
   避免询问薪资期望、职业规划或管理经验等非技术话题。

2. 人事面试官：应专注于软技能、文化契合度、职业发展规划等方面，
   绝对不应询问技术实现细节或专业技术问题。

3. 部门负责人：应关注管理能力、团队领导力、战略思维等管理层面问题，
   避免过于细节的技术实现问题。

4. 业务面试官：应关注业务理解、专业知识、解决方案能力等业务层面问题，
   避免深入技术实现细节。

确保每个面试官角色的问题都严格限定在其职责范围内，不要越界提问。
同时，确保所有问题都与候选人的具体情况和应聘职位高度相关。"""
        
        return role_prompts.get(role, default_prompt)

    async def generate_interview_guide_enhanced(
        self,
        db: Session,
        request: InterviewGuideRequest
    ) -> Dict[str, str]:
        """根据简历信息、职位信息、面试官角色和行业名称生成增强版面试指导文档
        
        Args:
            db: 数据库会话
            request: 面试指导请求对象
            
        Returns:
            包含生成内容的字典，格式为 {"content": "生成的面试指导文档内容"}
        """
        try:
            # 从请求对象中提取参数
            resume_id = request.resumeId
            job_id = request.jobId
            role = request.role
            industry = request.industry
            
            # 处理focusPoints字段
            focus_points = None
            if hasattr(request, 'focusPoints') and request.focusPoints:
                focus_points = request.focusPoints.content
            
            logger.info(
                f"开始生成增强版面试指导文档: resumeId={resume_id}, "
                f"jobId={job_id}, role={role}, industry={industry}"
            )
            
            # 1. 获取简历详情
            resume = await resume_service.get_resume_detail(
                db, 
                resume_id=resume_id
            )
            if not resume:
                raise HTTPException(status_code=404, detail="简历不存在")
            
            # 2. 获取职位详情
            job = await job_service.get_job_detail(
                db, 
                job_id=job_id
            )
            if not job:
                raise HTTPException(status_code=404, detail="职位不存在")
            
            logger.info("成功获取简历和职位信息")
            
            # 3. 构建系统提示词
            system_prompt = """你是一位专业的面试指导专家。请根据提供的候选人信息和职位要求，
生成一份详细且高度针对性的面试指导文档。

你的文档必须包含以下组成部分：
1. 候选人与职位匹配度分析：详细分析候选人的技能、经验与职位要求的匹配情况
2. 核心能力评估框架：根据职位要求设计评估维度和标准
3. 整合式面试问题与评估：对每个核心能力维度，将面试问题、参考答案和评分标准整合在一起展示

对于"整合式面试问题与评估"部分的格式要求：
- 按评估维度分类组织
- 对每个问题，必须同时包含以下内容：
  * 问题内容
  * 期望的参考答案要点
  * 回答质量评分标准
- 不要将问题、答案和评分标准分开成不同章节，而是整合在一起显示

所有问题和评估维度必须高度个性化，直接针对候选人的具体背景和职位要求。
避免泛泛而谈或通用模板式的问题。
"""

            # 获取行业特定的提示增强部分
            industry_prompt = self._get_industry_specific_prompt(
                industry=industry or "通用", 
                role=role
            )
            
            # 获取角色特定的提示
            role_prompt = self._get_role_prompt(role)
            
            # 合并提示词
            system_prompt = f"{system_prompt}\n\n{role_prompt}\n\n{industry_prompt}"
            
            # 4. 构建主要提示词
            prompt = f"""请为以下面试生成增强版指导文档：

候选人信息：
姓名：{resume.name}
当前职位：{resume.current_position or "未提供"}
工作年限：{resume.experience_years or "未提供"}
最高学历：{resume.highest_education or "未提供"}
技术栈：{self._format_skills(resume.skills)}

工作经历：
{self._format_work_experience(resume.work_experience)}

教育经历：
{self._format_education(resume.education)}

职位信息：
职位名称：{job.title}
部门：{job.department or "未提供"}
职位要求：
{self._format_job_requirements(job.requirements)}

面试官角色：{role}
行业领域：{industry or "通用"}
"""

            if focus_points:
                prompt += f"\n面试关注点：\n{focus_points}\n"

            prompt += """
请生成一份结构完整、高度定制化的面试指导文档，必须包含：

1. 候选人简历分析
   - 候选人整体背景评估
   - 与职位的匹配度分析
   - 优势与不足分析

2. 核心能力评估框架
   - 根据职位要求，设计3-5个关键评估维度
   - 每个维度的评估标准和重要性说明

3. 整合式面试问题与评估
   - 按评估维度分类组织面试问题（总计10-15个问题）
   - 每个问题必须将以下要素整合在一起展示（不要分成不同章节）：
     a. 问题内容（必须针对候选人具体背景设计）
     b. 参考答案要点
     c. 回答质量评分标准

4. 综合录用建议框架
   - 各维度权重建议
   - 总体评价指导

确保所有问题都与候选人背景高度相关，文档内容具体实用，能直接指导面试评估。
每个问题的问题、答案和评分标准必须放在一起显示，而不是分开成不同章节。
"""

            logger.info("提示词构建完成，开始调用LLM服务")

            # 5. 调用LLM服务生成文档
            llm_config = await llm_service.get_default_config(db)
            response = await llm_service.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                db=db,
                max_tokens=8000,  # 增加token限制以容纳参考答案和评分标准
                llm_config=llm_config  # 使用获取的配置
            )
            
            logger.info("增强版面试指导文档生成完成")
            
            return {"content": response["content"]}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"生成增强版面试指导文档失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"生成增强版面试指导文档失败: {str(e)}"
            )
    
    async def stream_interview_guide_enhanced(
        self,
        db: Session,
        request: InterviewGuideRequest,
    ) -> AsyncGenerator[str, None]:
        """流式生成增强版面试指导文档
        
        Args:
            db: 数据库会话
            request: 面试指导请求对象
            
        Returns:
            异步生成器，逐块返回生成的文档内容
        """
        try:
            # 从请求对象中提取参数
            resume_id = request.resumeId
            job_id = request.jobId
            role = request.role
            industry = request.industry
            
            # 处理focusPoints字段
            focus_points = None
            if hasattr(request, 'focusPoints') and request.focusPoints:
                focus_points = request.focusPoints.content
            
            logger.info(
                f"开始流式生成增强版面试指导文档: resumeId={resume_id}, "
                f"jobId={job_id}, role={role}, industry={industry}"
            )
            
            # 1. 获取简历详情
            resume = await resume_service.get_resume_detail(
                db, 
                resume_id=resume_id
            )
            if not resume:
                raise HTTPException(status_code=404, detail="简历不存在")
            
            # 2. 获取职位详情
            job = await job_service.get_job_detail(
                db, 
                job_id=job_id
            )
            if not job:
                raise HTTPException(status_code=404, detail="职位不存在")
            
            logger.info("成功获取简历和职位信息")
            
            # 3. 构建系统提示词
            system_prompt = """你是一位专业的面试指导专家。请根据提供的候选人信息和职位要求，
生成一份详细且高度针对性的面试指导文档。

你的文档必须包含以下组成部分：
1. 候选人与职位匹配度分析：详细分析候选人的技能、经验与职位要求的匹配情况
2. 核心能力评估框架：根据职位要求设计评估维度和标准
3. 整合式面试问题与评估：对每个核心能力维度，将面试问题、参考答案和评分标准整合在一起展示

对于"整合式面试问题与评估"部分的格式要求：
- 按评估维度分类组织
- 对每个问题，必须同时包含以下内容：
  * 问题内容
  * 期望的参考答案要点
  * 回答质量评分标准
- 不要将问题、答案和评分标准分开成不同章节，而是整合在一起显示

所有问题和评估维度必须高度个性化，直接针对候选人的具体背景和职位要求。
避免泛泛而谈或通用模板式的问题。
"""

            # 获取行业特定的提示增强部分
            industry_prompt = self._get_industry_specific_prompt(
                industry=industry or "通用", 
                role=role
            )
            
            # 获取角色特定的提示
            role_prompt = self._get_role_prompt(role)
            
            # 合并提示词
            system_prompt = f"{system_prompt}\n\n{role_prompt}\n\n{industry_prompt}"
            
            # 4. 构建主要提示词
            prompt = f"""请为以下面试生成增强版指导文档：

候选人信息：
姓名：{resume.name}
当前职位：{resume.current_position or "未提供"}
工作年限：{resume.experience_years or "未提供"}
最高学历：{resume.highest_education or "未提供"}
技术栈：{self._format_skills(resume.skills)}

工作经历：
{self._format_work_experience(resume.work_experience)}

教育经历：
{self._format_education(resume.education)}

职位信息：
职位名称：{job.title}
部门：{job.department or "未提供"}
职位要求：
{self._format_job_requirements(job.requirements)}

面试官角色：{role}
行业领域：{industry or "通用"}
"""

            if focus_points:
                prompt += f"\n面试关注点：\n{focus_points}\n"

            prompt += """
请生成一份结构完整、高度定制化的面试指导文档，必须包含：

1. 候选人简历分析
   - 候选人整体背景评估
   - 与职位的匹配度分析
   - 优势与不足分析

2. 核心能力评估框架
   - 根据职位要求，设计3-5个关键评估维度
   - 每个维度的评估标准和重要性说明

3. 整合式面试问题与评估
   - 按评估维度分类组织面试问题（总计10-15个问题）
   - 每个问题必须将以下要素整合在一起展示（不要分成不同章节）：
     a. 问题内容（必须针对候选人具体背景设计）
     b. 参考答案要点
     c. 回答质量评分标准

4. 综合录用建议框架
   - 各维度权重建议
   - 总体评价指导

确保所有问题都与候选人背景高度相关，文档内容具体实用，能直接指导面试评估。
每个问题的问题、答案和评分标准必须放在一起显示，而不是分开成不同章节。
"""

            logger.info("提示词构建完成，开始流式生成")

            # 5. 调用LLM服务流式生成文档
            llm_config = await llm_service.get_default_config(db)
            logger.info(f"获取LLM配置成功，使用模型: {llm_config.chat_model}")

            async for chunk in llm_service.stream_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                llm_config=llm_config,
                max_tokens=8000  # 增加token限制以容纳参考答案和评分标准
            ):
                yield chunk
            
            logger.info("增强版面试指导文档生成完成")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"流式生成增强版面试指导文档失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"生成增强版面试指导文档失败: {str(e)}"
            )

    async def generate_interview_guide(
        self,
        db: Session,
        request: InterviewGuideRequest
    ) -> Dict[str, Any]:
        """生成面试指导文档（已弃用，请使用 generate_interview_guide_enhanced）"""
        logger.warning(
            "generate_interview_guide 方法已弃用，"
            "请使用 generate_interview_guide_enhanced"
        )
        
        # 将请求转发到增强版方法
        return await self.generate_interview_guide_enhanced(
            db=db,
            request=request
        )
    
    async def stream_interview_guide(
        self,
        db: Session,
        request: InterviewGuideRequest
    ) -> AsyncGenerator[str, None]:
        """流式生成面试指导文档（已弃用，请使用 stream_interview_guide_enhanced）"""
        logger.warning(
            "stream_interview_guide 方法已弃用，"
            "请使用 stream_interview_guide_enhanced"
        )
        
        # 将请求转发到增强版方法
        async for chunk in self.stream_interview_guide_enhanced(
            db=db,
            request=request
        ):
            yield chunk

    async def get_industry_role_template(
        self,
        db: Session,
        industry: str,
        role: str,
        position: str
    ) -> Dict[str, str]:
        """获取特定行业、角色和职位的面试指导通用模板
        
        该方法首先基于行业、面试官角色和职位名称生成通用的面试指导模板，
        不涉及具体候选人信息，可作为缓存模板供后续快速定制化使用。
        
        Args:
            db: 数据库会话
            industry: 行业名称，如'信息技术'、'金融'等
            role: 面试官角色，如'技术面试官'、'部门负责人'等 
            position: 职位名称，如'后端工程师'、'产品经理'等
            
        Returns:
            包含生成内容的字典，格式为 {"content": "生成的面试指导模板内容"}
        """
        try:
            logger.info(
                f"开始生成行业职位模板: industry={industry}, "
                f"role={role}, position={position}"
            )
            
            # 获取行业特定的提示增强部分
            industry_prompt = self._get_industry_specific_prompt(
                industry=industry, 
                role=role
            )
            
            # 获取角色特定的提示
            role_prompt = self._get_role_prompt(role)
            
            # 构建系统提示词，指导模型如何生成面试模板
            system_prompt = """你是一位专业的面试指导专家，擅长为各行业和职位创建结构化的面试评估框架。
你的任务是创建一个面试指导模板，用于评估特定行业和职位的候选人。

该模板必须遵循以下原则：
1. 高度针对特定行业和职位要求，包含行业专业术语和评估标准
2. 严格符合面试官角色的评估范围和关注点，不越界提问
3. 提供明确的结构化评估框架，便于后续定制化使用
4. 包含与职位直接相关的核心能力评估维度
5. 设计针对性的面试问题框架和评估标准
6. 包含从面试官角色视角的候选人与职位匹配度分析框架
7. 要求对候选人相对该职位的优势和劣势进行全面分析

你的面试指导模板必须易于理解和操作，能够作为面试官评估候选人的实用工具。模板应当包含评估候选人是否满足岗位要求的所有必要维度，既考察专业能力，也关注综合素质。最终评估必须能够清晰呈现候选人是否适合该职位，以及适合的具体理由。
"""

            system_prompt = f"{system_prompt}\n\n{role_prompt}\n\n{industry_prompt}"
            
            # 构建主要提示词
            prompt = f"""请创建一个适用于{industry}行业{position}职位的面试指导模板，面试官角色为{role}。

这个模板将用于指导面试官对候选人进行全面评估，后续会结合具体候选人的简历信息进行个性化定制。请设计一个完整的面试指导文档结构，包括以下必要部分：

# 面试指导模板框架

## 一、候选人与职位匹配度分析
- {industry}行业{position}职位核心能力匹配度评估框架
- 专业背景与经验评估维度
- 候选人相对职位的优势分析框架
- 候选人相对职位的不足分析框架
- 从{role}角度评估的关键匹配指标

## 二、核心能力评估维度
- [设计4-6个针对{position}职位的核心能力评估维度]
- [每个维度应明确对应的评估标准和权重]
- [面试官应如何判断候选人在各维度的表现]

## 三、专业经验验证方向
- [针对{position}的关键经验验证要点]
- [行业特定知识考察领域]
- [案例分析与问题解决能力验证]
- [如何辨别候选人经验的真实性和深度]

## 四、面试问题框架
- [按评估维度分类的问题框架，每个维度3-4个问题类型]
- [问题应包含评估目的、期望回答要点和参考答案]
- [设计深入追问路径]
- [根据候选人回答判断其优劣势的指导]

## 五、评估标准与决策框架
- [明确的评分标准，包括各维度的权重]
- [录用决策依据]
- [风险信号识别标准]
- [候选人优劣势综合评价框架]
- [最终匹配度评估指南]

生成的模板必须：
1. 充分体现{industry}行业特点和{position}职位要求
2. 严格符合{role}的评估视角和职责范围
3. 框架清晰，便于后续个性化定制
4. 提供明确的评估维度和标准
5. 包含适合{role}角色的问题类型和评估重点
6. 提供候选人优势和劣势分析的明确框架
7. 能够从{role}独特视角评估候选人与职位的真实匹配程度

请直接返回完整的Markdown格式模板结构，包括章节标题和关键评估点，但不需要包含具体问题内容，只提供问题框架和类型。
"""

            # 调用LLM服务生成模板
            llm_config = await llm_service.get_default_config(db)
            response = await llm_service.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                db=db,
                max_tokens=2000,  # 减少token用量，因为我们只需要框架
                llm_config=llm_config
            )
            
            logger.info("行业职位面试指导模板生成完成")
            
            return {"content": response["content"]}
            
        except Exception as e:
            logger.error(f"生成行业职位面试指导模板失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"生成行业职位面试指导模板失败: {str(e)}"
            )

    async def generate_interview_guide_two_stage(
        self,
        db: Session,
        request: InterviewGuideRequest,
        template: str = None
    ) -> Dict[str, str]:
        """两阶段生成面试指导文档：先获取模板，再定制化
        
        该方法采用两阶段生成方式：
        1. 如果没有提供模板，先基于行业、角色和职位生成通用模板
        2. 结合模板、候选人简历和职位要求生成定制化的面试指导文档
        
        Args:
            db: 数据库会话
            request: 面试指导请求对象，包含简历ID、职位ID、角色、行业等信息
            template: 预先生成的面试指导模板，可选
            
        Returns:
            包含生成内容的字典，格式为 {"content": "生成的面试指导文档内容"}
        """
        try:
            logger.info(
                f"开始两阶段生成面试指导文档: request={request}"
            )
            
            # 调用详细参数版本的方法
            return await self.generate_interview_guide_two_stage_impl(
                db=db,
                request=request,
                template=template
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"两阶段生成面试指导文档失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"两阶段生成面试指导文档失败: {str(e)}"
            )

    async def generate_interview_guide_two_stage_impl(
        self,
        db: Session,
        request: InterviewGuideRequest,
        template: str = None
    ) -> Dict[str, str]:
        """两阶段生成面试指导文档的具体实现
        
        Args:
            db: 数据库会话
            request: 面试指导请求对象
            template: 预先生成的面试指导模板，可选
            
        Returns:
            包含生成内容的字典，格式为 {"content": "生成的面试指导文档内容"}
        """
        try:
            # 从请求对象中提取参数
            resume_id = request.resumeId
            job_id = request.jobId
            role = request.role
            industry = request.industry
            
            # 处理focusPoints字段
            focus_points = None
            if hasattr(request, 'focusPoints') and request.focusPoints:
                focus_points = request.focusPoints.content
            
            logger.info(
                f"开始两阶段生成面试指导具体实现: resumeId={resume_id}, "
                f"jobId={job_id}, role={role}, industry={industry}"
            )
            
            # 1. 获取简历详情
            resume = await resume_service.get_resume_detail(
                db, 
                resume_id=resume_id
            )
            if not resume:
                raise HTTPException(status_code=404, detail="简历不存在")
            
            # 2. 获取职位详情
            job = await job_service.get_job_detail(
                db, 
                job_id=job_id
            )
            if not job:
                raise HTTPException(status_code=404, detail="职位不存在")
            
            # 3. 第一阶段：获取或生成模板
            if not template:
                # 使用职位名称、行业和角色生成通用模板
                template_result = await self.get_industry_role_template(
                    db=db,
                    industry=industry or "通用",
                    role=role,
                    position=job.title
                )
                template = template_result["content"]
                
                logger.info("成功生成行业职位模板")
            
            # 4. 第二阶段：基于模板和简历信息定制化
            system_prompt = """你是一位专业的面试指导专家。请根据提供的候选人信息、职位要求和面试模板，
生成一份高度个性化的面试指导文档。

你的任务是将通用的面试模板与候选人的具体情况结合起来，生成一份定制化的面试指导文档。
请特别关注：
1. 根据候选人的技能、经验和背景定制面试问题，问题必须直接针对其简历中的具体经历
2. 结合候选人的特点完善评分标准，提供针对其优势和弱点的具体评判依据
3. 为面试官提供针对该特定候选人的详细指导，包括重点追问方向和验证方法
4. 确保所有问题和评估维度都高度契合候选人情况，突出行业特定的考察重点
5. 明确提供针对此候选人的面试关注点清单，至少包含10个具体观察指标

面试指导文档必须：
1. 高度体现行业专业性，使用行业术语和评估标准
2. 符合面试官角色的评估视角和关注重点
3. 同时评估候选人的硬技能和软技能
4. 包含明确的面试过程中的观察重点和决策依据
5. 提供清晰具体的评分标准和录用建议框架

最终文档应保留模板的整体结构，但内容必须完全定制化，能指导面试官针对性地评估该候选人。
"""

            # 获取行业特定的提示增强部分
            industry_prompt = self._get_industry_specific_prompt(
                industry=industry or "通用", 
                role=role
            )
            
            # 组合系统提示词
            system_prompt = f"{system_prompt}\n\n{industry_prompt}"
            
            # 构建主要提示词
            prompt = f"""请基于以下面试模板和候选人信息，生成高度定制化的面试指导文档：

==== 面试模板开始 ====
{template}
==== 面试模板结束 ====

候选人信息：
姓名：{resume.name}
当前职位：{resume.current_position or "未提供"}
工作年限：{resume.experience_years or "未提供"}
最高学历：{resume.highest_education or "未提供"}
技术栈：{self._format_skills(resume.skills)}

工作经历：
{self._format_work_experience(resume.work_experience)}

教育经历：
{self._format_education(resume.education)}

职位信息：
职位名称：{job.title}
部门：{job.department or "未提供"}
职位要求：
{self._format_job_requirements(job.requirements)}

面试官角色：{role}
行业领域：{industry or "通用"}
"""

            if focus_points:
                prompt += f"""
额外面试关注点：
{focus_points}

请将上述关注点整合到面试指导中，作为重点考察方向。
"""

            prompt += """
请基于上述模板的整体结构，生成一份高度定制化的面试指导文档。要求：

1. 保持模板的评估维度框架，但完全根据候选人情况定制内容
2. 所有面试问题必须与候选人背景高度相关，针对其特定经历设计具体问题
3. 评分标准应根据候选人背景和职位要求调整，明确指出各等级具体表现
4. 添加一个专门的"面试关键观察点"部分，列出至少10个针对此候选人的具体观察指标
5. 每个问题必须明确说明评估目的和关注点，以及深入追问方向
6. 为面试官提供针对这位特定候选人的综合评估框架和决策指南

所有内容必须：
- 与行业高度相关，体现行业专业性和评估标准
- 符合面试官角色的评估视角和关注重点
- 针对候选人的具体情况，不可泛泛而谈
- 使用专业、准确的行业术语和评估指标
- 提供清晰的决策依据和标准
"""

            # 调用LLM服务生成文档
            llm_config = await llm_service.get_default_config(db)
            response = await llm_service.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                db=db,
                max_tokens=8000,
                llm_config=llm_config
            )
            
            logger.info("两阶段面试指导文档生成完成")
            
            return {"content": response["content"]}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"两阶段生成面试指导文档实现失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"两阶段生成面试指导文档失败: {str(e)}"
            )

    async def stream_interview_guide_two_stage(
        self,
        db: Session,
        request: InterviewGuideRequest,
        template: str = None
    ) -> AsyncGenerator[str, None]:
        """流式两阶段生成面试指导文档：先获取模板，再定制化
        
        该方法采用两阶段生成方式，并以流式方式返回结果：
        1. 如果没有提供模板，先基于行业、角色和职位生成通用模板
        2. 结合模板、候选人简历和职位要求流式生成定制化的面试指导文档
        
        Args:
            db: 数据库会话
            request: 面试指导请求对象，包含简历ID、职位ID、角色、行业等信息
            template: 预先生成的面试指导模板，可选
            
        Returns:
            异步生成器，逐块返回生成的文档内容
        """
        try:
            logger.info(
                f"开始流式两阶段生成面试指导文档: request={request}"
            )
            
            # 从请求对象中提取参数
            resume_id = request.resumeId
            job_id = request.jobId
            role = request.role
            industry = request.industry
            
            # 处理focusPoints字段
            focus_points = None
            if hasattr(request, 'focusPoints') and request.focusPoints:
                focus_points = request.focusPoints.content
            
            # 1. 获取简历详情
            resume = await resume_service.get_resume_detail(
                db, 
                resume_id=resume_id
            )
            if not resume:
                raise HTTPException(status_code=404, detail="简历不存在")
            
            # 2. 获取职位详情
            job = await job_service.get_job_detail(
                db, 
                job_id=job_id
            )
            if not job:
                raise HTTPException(status_code=404, detail="职位不存在")
            
            # 3. 第一阶段：获取或生成模板
            if not template:
                # 使用职位名称、行业和角色生成通用模板
                template_result = await self.get_industry_role_template(
                    db=db,
                    industry=industry or "通用",
                    role=role,
                    position=job.title
                )
                template = template_result["content"]
                
                logger.info(f"成功生成行业职位模板: {template}")
            
            # 4. 第二阶段：基于模板和简历信息定制化
            system_prompt = """你是一位专业的面试指导专家。请根据提供的候选人信息、职位要求和面试模板，
生成一份高度个性化的面试指导文档。

你的任务是将通用的面试模板与候选人的具体情况结合起来，生成一份定制化的面试指导文档。
请特别关注：
1. 根据候选人的技能、经验和背景定制面试问题，问题必须直接针对其简历中的具体经历
2. 结合候选人的特点完善评分标准，提供针对其优势和弱点的具体评判依据
3. 为面试官提供针对该特定候选人的详细指导，包括重点追问方向和验证方法
4. 确保所有问题和评估维度都高度契合候选人情况，突出行业特定的考察重点
5. 明确提供针对此候选人的面试关注点清单，至少包含10个具体观察指标

面试指导文档必须：
1. 高度体现行业专业性，使用行业术语和评估标准
2. 符合面试官角色的评估视角和关注重点
3. 同时评估候选人的硬技能和软技能
4. 包含明确的面试过程中的观察重点和决策依据
5. 提供清晰具体的评分标准和录用建议框架

最终文档应保留模板的整体结构，但内容必须完全定制化，能指导面试官针对性地评估该候选人。
"""

            # 获取行业特定的提示增强部分
            industry_prompt = self._get_industry_specific_prompt(
                industry=industry or "通用", 
                role=role
            )
            
            # 组合系统提示词
            system_prompt = f"{system_prompt}\n\n{industry_prompt}"
            
            # 构建主要提示词
            prompt = f"""请基于以下面试模板和候选人信息，生成高度定制化的面试指导文档：

==== 面试模板开始 ====
{template}
==== 面试模板结束 ====

候选人信息：
姓名：{resume.name}
当前职位：{resume.current_position or "未提供"}
工作年限：{resume.experience_years or "未提供"}
最高学历：{resume.highest_education or "未提供"}
技术栈：{self._format_skills(resume.skills)}

工作经历：
{self._format_work_experience(resume.work_experience)}

教育经历：
{self._format_education(resume.education)}

职位信息：
职位名称：{job.title}
部门：{job.department or "未提供"}
职位要求：
{self._format_job_requirements(job.requirements)}

面试官角色：{role}
行业领域：{industry or "通用"}
"""

            if focus_points:
                prompt += f"""
额外面试关注点：
{focus_points}

请将上述关注点整合到面试指导中，作为重点考察方向。
"""

            prompt += """
请基于上述模板的整体结构，生成一份高度定制化的面试指导文档。要求：

1. 保持模板的评估维度框架，但完全根据候选人情况定制内容
2. 所有面试问题必须与候选人背景高度相关，针对其特定经历设计具体问题
3. 评分标准应根据候选人背景和职位要求调整，明确指出各等级具体表现
4. 添加一个专门的"面试关键观察点"部分，列出至少10个针对此候选人的具体观察指标
5. 每个问题必须明确说明评估目的和关注点，以及深入追问方向
6. 为面试官提供针对这位特定候选人的综合评估框架和决策指南

所有内容必须：
- 与行业高度相关，体现行业专业性和评估标准
- 符合面试官角色的评估视角和关注重点
- 针对候选人的具体情况，不可泛泛而谈
- 使用专业、准确的行业术语和评估指标
- 提供清晰的决策依据和标准
"""

            # 流式调用LLM服务生成文档
            llm_config = await llm_service.get_default_config(db)
            
            async for chunk in llm_service.stream_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                llm_config=llm_config,
                max_tokens=8000
            ):
                yield chunk
            
            logger.info("流式两阶段面试指导文档生成完成")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"流式两阶段生成面试指导文档失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"流式两阶段生成面试指导文档失败: {str(e)}"
            )

# 创建服务实例
interview_ai_service = InterviewAIService()

# 只导出实例
__all__ = ["interview_ai_service"] 