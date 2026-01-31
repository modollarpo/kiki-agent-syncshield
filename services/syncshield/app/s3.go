package main

import (
	"bytes"
	"context"
	"os"
	"time"

	"kiki-agent-syncshield/app/handlers"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

var s3Client *s3.Client
var s3Bucket string

func InitS3() error {
	bucket := os.Getenv("SYNC_S3_BUCKET")
	if bucket == "" {
		bucket = "syncshield-audit-logs"
	}
	s3Bucket = bucket
	cfg, err := config.LoadDefaultConfig(context.Background())
	if err != nil {
		return err
	}
	s3Client = s3.NewFromConfig(cfg)
	return nil
}

func SaveAuditLogToS3(entry handlers.AuditLogEntry) error {
	if s3Client == nil || s3Bucket == "" {
		return nil // S3 not configured
	}
	key := "audit/" + entry.UserID + "/" + entry.Event + "/" + time.Now().Format("20060102T150405") + ".log"
	body := []byte(entry.Encrypted)
	_, err := s3Client.PutObject(context.Background(), &s3.PutObjectInput{
		Bucket: aws.String(s3Bucket),
		Key:    aws.String(key),
		Body:   bytes.NewReader(body),
	})
	return err
}
