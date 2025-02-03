# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa

# Import all models here for Alembic
from app.models.user import User  # noqa
from app.models.candidate import Candidate  # noqa
from app.models.interview import Interview  # noqa
from app.models.job import Job  # noqa 