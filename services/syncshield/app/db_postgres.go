package main

import (
	"context"
	"os"
	"time"

	"kiki-agent-syncshield/app/handlers"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var db *gorm.DB

func InitDB() error {
	dsn := os.Getenv("SYNC_DB_DSN")
	if dsn == "" {
		dsn = "host=postgres user=postgres password=kiki_pass dbname=syncshield port=5432 sslmode=disable"
	}
	database, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		return err
	}
	db = database
	return db.AutoMigrate(&AuditLogModel{})
}

func SaveAuditLogToDB(entry handlers.AuditLogEntry) error {
	model := AuditLogModel{
		Encrypted: entry.Encrypted,
		UserID:    entry.UserID,
		Event:     entry.Event,
		Timestamp: entry.Timestamp,
		CreatedAt: time.Now().UnixMilli(),
	}
	return db.WithContext(context.Background()).Create(&model).Error
}

func QueryAuditLogsFromDB(user, event string) ([]AuditLogModel, error) {
	var logs []AuditLogModel
	q := db.Model(&AuditLogModel{})
	if user != "" {
		q = q.Where("user_id = ?", user)
	}
	if event != "" {
		q = q.Where("event = ?", event)
	}
	if err := q.Order("timestamp desc").Find(&logs).Error; err != nil {
		return nil, err
	}
	return logs, nil
}
