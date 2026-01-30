package main

type AuditLogModel struct {
	ID        uint   `gorm:"primaryKey"`
	Encrypted string `gorm:"column:encrypted;type:text;not null"`
	UserID    string `gorm:"column:user_id;type:varchar(64);index"`
	Event     string `gorm:"column:event;type:varchar(64);index"`
	Timestamp int64  `gorm:"column:timestamp;index"`
	CreatedAt int64  `gorm:"autoCreateTime:milli"`
}

func (AuditLogModel) TableName() string {
	return "audit_logs"
}
