from ..models import db, Project

class ProjectService:
    @staticmethod
    def get_all():
        return Project.query.order_by(Project.updated_at.desc()).all()
    
    @staticmethod
    def get(project_id):
        return Project.query.get_or_404(project_id)
    
    @staticmethod
    def create(data):
        project = Project(**data)
        db.session.add(project)
        db.session.commit()
        return project
    
    @staticmethod
    def update(project_id, data):
        project = Project.query.get_or_404(project_id)
        for key, value in data.items():
            if hasattr(project, key):
                setattr(project, key, value)
        db.session.commit()
        return project
    
    @staticmethod
    def delete(project_id):
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()

project_service = ProjectService()
