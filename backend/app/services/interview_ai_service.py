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
            system_prompt = """你是面试结构设计专家，请根据候选人和职位信息为特定角色设计最合适的面试文档结构。
设计时请考虑:
1. 面试官角色的关注点和职责
2. 候选人经验与职位的匹配度
3. 行业特点(如有提供)
4. 必要的评估维度和具体面试问题类型

返回结构应采用Markdown格式，清晰列出章节和子项。只提供结构框架，不需包含具体内容。"""

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

    async def generate_interview_guide(
        self,
        db: Session,
        request: InterviewGuideRequest
    ) -> Dict[str, Any]:
        """生成面试指导文档"""
        try:
            logger.info(
                f"开始生成面试指导文档: resumeId={request.resumeId}, "
                f"jobId={request.jobId}"
            )
            
            # 1. 获取简历详情
            resume = await resume_service.get_resume_detail(
                db, 
                resume_id=request.resumeId
            )
            if not resume:
                raise HTTPException(status_code=404, detail="简历不存在")
            
            # 2. 获取职位详情
            job = await job_service.get_job_detail(
                db, 
                job_id=request.jobId
            )
            if not job:
                raise HTTPException(status_code=404, detail="职位不存在")
            
            logger.info("成功获取简历和职位信息")
            
            # 3. 构建系统提示词
            base_system_prompt = """你是一位专业的面试指导专家。请根据提供的候选人信息和职位要求，
生成一份详细且高度针对性的面试指导文档。"""

            # 获取行业特定的提示增强部分
            industry_prompt = self._get_industry_specific_prompt(
                industry=request.industry or "通用", 
                role=request.role
            )
            
            # 使用LLM生成自适应文档结构
            try:
                logger.info("开始生成自适应文档结构")
                adaptive_structure = await self.get_adaptive_structure(
                    db=db,
                    resume=resume,
                    job=job,
                    role=request.role,
                    industry=request.industry
                )
                logger.info("自适应文档结构生成成功")
                
                # 构建面试官角色提示词
                role_prompt = self._get_role_prompt(request.role)
                
                # 构建完整的系统提示词，使用自适应结构
                system_prompt = (
                    f"{base_system_prompt}\n\n"
                    f"{role_prompt}\n\n"
                    f"{industry_prompt}\n\n"
                    f"请按照以下结构生成文档：\n\n{adaptive_structure}"
                )
            except Exception as e:
                logger.error(f"自适应结构生成失败，使用默认结构: {str(e)}", exc_info=True)
                
                # 如果自适应结构生成失败，回退到使用预定义的结构
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
                
                # 获取角色特定的内容
                role_content = role_specific_content.get(
                    request.role, 
                    role_specific_content["其他"]
                )
                
                # 构建完整的系统提示词，包含行业特定部分
                system_prompt = (
                    f"{base_system_prompt}\n\n"
                    f"{role_content['prompt']}\n\n"
                    f"{industry_prompt}\n\n"
                    f"{role_content['structure']}"
                )

            # 4. 构建主要提示词
            prompt = f"""请为以下面试生成指导文档：

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

面试官角色：{request.role}
行业领域：{request.industry or "通用"}

面试关注点：
{request.focusPoints.content}

请根据以上信息，生成一份高度定制化的面试指导文档。特别注意：
1. 面试问题必须基于候选人的具体技术栈和项目经历精确设计
2. 评估要点应直接对应招聘职位的具体要求
3. 所有分析和问题必须与候选人和职位的实际情况紧密结合
4. 根据面试官角色({request.role})和行业领域({request.industry or "通用"})定制文档结构和内容深度
5. 确保问题同时具有针对性和深度，不可过于笼统
6. 为每个问题提供针对此候选人情况的参考答案和评分要点"""

            logger.info("提示词构建完成，开始调用LLM服务")

            # 5. 调用LLM服务生成文档
            response = await llm_service.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                db=db,
                max_tokens=8000  # 确保生成足够长的文档，增加token限制以容纳参考答案
            )
            
            logger.info("面试指导文档生成完成")
            
            return {"content": response["content"]}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"生成面试指导文档失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"生成面试指导文档失败: {str(e)}"
            )
            
    def _get_role_prompt(self, role: str) -> str:
        """获取面试官角色的基本提示词
        
        Args:
            role: 面试官角色
            
        Returns:
            角色提示词
        """
        role_prompts = {
            "部门负责人": """作为部门负责人，你应更关注：
1. 候选人的管理潜力和领导能力
2. 技术视野和战略思维
3. 跨部门协作能力
4. 项目管理和资源调配能力
5. 团队建设和人才培养能力

评估时，请特别关注候选人简历中显示的管理经验、团队规模、项目复杂度等信息，
并与招聘职位的管理要求进行匹配分析。

在设计面试问题时，应重点考察候选人的大局观、决策能力和管理思路，
确保问题针对候选人的具体背景和应聘职位，而不是泛泛而谈。""",

            "技术面试官": """作为技术面试官，你应更关注：
1. 候选人的技术深度和广度
2. 核心技术原理的理解
3. 系统设计和架构能力
4. 代码质量和编程思维
5. 技术问题解决能力

评估时，请详细分析候选人简历中的技术栈、项目经验和技术关键词，
将其与招聘职位要求的技术能力进行针对性匹配。

在设计面试问题时，应基于候选人的实际技术背景和项目经历设计有深度的问题，
确保问题聚焦在与应聘职位最相关的技术领域。""",

            "人事面试官": """作为人事面试官，你应更关注：
1. 候选人的沟通表达能力
2. 团队协作和人际关系处理
3. 职业规划和发展动机
4. 文化契合度和价值观
5. 学习能力和适应能力

评估时，请关注候选人的职业轨迹、跳槽原因、团队角色等信息，
判断其是否符合公司文化和团队氛围。

在设计面试问题时，应结合候选人简历中的经历和职位需求设计情景化问题，
评估候选人在实际工作环境中的软技能表现和适应能力。""",

            "业务面试官": """作为业务面试官，你应更关注：
1. 候选人对业务领域的理解深度
2. 行业经验和专业知识水平
3. 业务问题分析和解决能力
4. 业务决策和判断能力
5. 业务创新思维和市场敏感度

评估时，请关注候选人在相关业务领域的经验、项目成果和专业见解，
判断其是否具备所需的业务能力和发展潜力。

在设计面试问题时，应结合行业特点和职位要求，设计案例分析和情景应对问题，
评估候选人在实际业务场景中的表现能力。"""
        }
        
        default_prompt = """请根据面试官的具体角色，调整面试关注点和问题设计。

评估时，应全面分析候选人简历与职位要求的匹配度，找出需要重点考察的领域。

确保问题既能考察候选人的专业能力，又能满足特定角色的评估需求，
且所有问题都应直接针对候选人的具体情况和应聘职位制定。"""
        
        return role_prompts.get(role, default_prompt)

    async def stream_interview_guide(
        self,
        db: Session,
        request: InterviewGuideRequest
    ) -> AsyncGenerator[str, None]:
        """流式生成面试指导文档"""
        try:
            logger.info(
                f"开始流式生成面试指导文档: resumeId={request.resumeId}, "
                f"jobId={request.jobId}"
            )
            
            # 1. 获取简历详情
            resume = await resume_service.get_resume_detail(
                db, 
                resume_id=request.resumeId
            )
            if not resume:
                raise HTTPException(status_code=404, detail="简历不存在")
            
            # 2. 获取职位详情
            job = await job_service.get_job_detail(
                db, 
                job_id=request.jobId
            )
            if not job:
                raise HTTPException(status_code=404, detail="职位不存在")
            
            logger.info("成功获取简历和职位信息")
            
            # 3. 构建系统提示词
            base_system_prompt = """你是一位专业的面试指导专家。请根据提供的候选人信息和职位要求，
生成一份详细且高度针对性的面试指导文档。"""

            # 获取行业特定的提示增强部分
            industry_prompt = self._get_industry_specific_prompt(
                industry=request.industry or "通用", 
                role=request.role
            )
            
            # 使用LLM生成自适应文档结构
            try:
                logger.info("开始生成自适应文档结构")
                adaptive_structure = await self.get_adaptive_structure(
                    db=db,
                    resume=resume,
                    job=job,
                    role=request.role,
                    industry=request.industry
                )
                logger.info("自适应文档结构生成成功")
                
                # 构建面试官角色提示词
                role_prompt = self._get_role_prompt(request.role)
                
                # 构建完整的系统提示词，使用自适应结构
                system_prompt = (
                    f"{base_system_prompt}\n\n"
                    f"{role_prompt}\n\n"
                    f"{industry_prompt}\n\n"
                    f"请按照以下结构生成文档：\n\n{adaptive_structure}"
                )
            except Exception as e:
                logger.error(f"自适应结构生成失败，使用默认结构: {str(e)}", exc_info=True)
                
                # 如果自适应结构生成失败，回退到使用预定义的结构
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
                
                # 获取角色特定的内容
                role_content = role_specific_content.get(
                    request.role, 
                    role_specific_content["其他"]
                )
                
                # 构建完整的系统提示词，包含行业特定部分
                system_prompt = (
                    f"{base_system_prompt}\n\n"
                    f"{role_content['prompt']}\n\n"
                    f"{industry_prompt}\n\n"
                    f"{role_content['structure']}"
                )

            # 4. 构建主要提示词
            prompt = f"""请为以下面试生成指导文档：

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

面试官角色：{request.role}
行业领域：{request.industry or "通用"}

面试关注点：
{request.focusPoints.content}

请根据以上信息，生成一份高度定制化的面试指导文档。特别注意：
1. 面试问题必须基于候选人的具体技术栈和项目经历精确设计
2. 评估要点应直接对应招聘职位的具体要求
3. 所有分析和问题必须与候选人和职位的实际情况紧密结合
4. 根据面试官角色({request.role})和行业领域({request.industry or "通用"})定制文档结构和内容深度
5. 确保问题同时具有针对性和深度，不可过于笼统
6. 为每个问题提供针对此候选人情况的参考答案和评分要点"""

            logger.info("提示词构建完成，开始流式生成")

            # 获取LLM配置
            llm_config = await llm_service.get_default_config(db)
            logger.info(f"获取LLM配置成功，使用模型: {llm_config.chat_model}")

            # 5. 调用LLM服务流式生成文档
            async for chunk in llm_service.stream_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                llm_config=llm_config,  # 添加LLM配置参数
                max_tokens=8000  # 确保生成足够长的文档，增加token限制以容纳参考答案
            ):
                yield chunk
            
            logger.info("面试指导文档生成完成")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"生成面试指导文档失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"生成面试指导文档失败: {str(e)}"
            )

# 创建服务实例
interview_ai_service = InterviewAIService()

# 只导出实例
__all__ = ["interview_ai_service"] 