# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa

# Import all models here for Alembic
from app.models.user import User  # noqa
# from app.models.candidate import Candidate  # noqa - 已废弃，请使用Talent模型
from app.models.interview import Interview  # noqa
from app.models.job import Job  # noqa
from app.models.resume import Resume  # noqa
from app.models.resume_repository import ResumeRepository  # noqa
from app.models.talent import Talent  # noqa
from app.models.trial_application import TrialApplication  # noqa 