package safefail

import (
	"log"
	"os"
	"time"
)

// AuditLogger logs all rollback and SafeFail events for compliance.
type AuditLogger struct {
	file *os.File
}

func NewAuditLogger(path string) (*AuditLogger, error) {
	f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return nil, err
	}
	return &AuditLogger{file: f}, nil
}

func (a *AuditLogger) Log(event, detail string) {
	timestamp := time.Now().Format(time.RFC3339)
	msg := timestamp + " [SafeFail] " + event + ": " + detail + "\n"
	a.file.WriteString(msg)
	log.Print(msg)
}

func (a *AuditLogger) Close() {
	a.file.Close()
}
