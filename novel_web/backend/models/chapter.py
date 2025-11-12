from datetime import datetime
from ..database import db

class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    outline_chapter_id = db.Column(db.Integer, db.ForeignKey('outline_chapters.id'), nullable=False)
    content = db.Column(db.Text)
    word_count = db.Column(db.Integer, default=0)
    quality_score = db.Column(db.Float)
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'outline_chapter_id': self.outline_chapter_id,
            'content': self.content,
            'word_count': self.word_count,
            'quality_score': self.quality_score,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
