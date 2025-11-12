from datetime import datetime
from ..database import db

class Annotation(db.Model):
    __tablename__ = 'annotations'
    
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(20), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='idea')
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'content': self.content,
            'type': self.type,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
