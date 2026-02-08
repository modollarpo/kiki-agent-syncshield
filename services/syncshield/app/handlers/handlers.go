package handlers

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/base64"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	otel "go.opentelemetry.io/otel"
)

// Production-grade audit log and AES-256 key management
type AuditLogEntry struct {
	Encrypted     string
	UserID        string
	Event         string
	Timestamp     int64
	SourceIP      string
	ComplianceTag string
}

// Use external immutable audit store (e.g., PostgreSQL, MinIO/S3)
var ExternalAuditStore []AuditLogEntry

// AES-256 key management: Use secure vault integration (e.g., HashiCorp Vault)
var AESKey []byte // Loaded securely at startup

var Tracer = otel.Tracer("syncshield")

// Request types

// AuditRequest is the payload for /audit
// RiskScanRequest is the payload for /risk-scan
type AuditRequest struct {
	Event  string                 `json:"event"`
	UserID string                 `json:"user_id"`
	Data   map[string]interface{} `json:"data"`
}

type RiskScanRequest struct {
	Data map[string]interface{} `json:"data"`
}

func EncryptAES256(plaintext string) (string, error) {
	block, err := aes.NewCipher(AESKey)
	if err != nil {
		return "", err
	}
	ciphertext := make([]byte, aes.BlockSize+len(plaintext))
	iv := ciphertext[:aes.BlockSize]
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return "", err
	}
	stream := cipher.NewCFBEncrypter(block, iv)
	stream.XORKeyStream(ciphertext[aes.BlockSize:], []byte(plaintext))
	return base64.StdEncoding.EncodeToString(ciphertext), nil
}

func DecryptAES256(ciphertextB64 string) (string, error) {
	ciphertext, err := base64.StdEncoding.DecodeString(ciphertextB64)
	if err != nil {
		return "", err
	}
	block, err := aes.NewCipher(AESKey)
	if err != nil {
		return "", err
	}
	if len(ciphertext) < aes.BlockSize {
		return "", err
	}
	iv := ciphertext[:aes.BlockSize]
	ciphertext = ciphertext[aes.BlockSize:]
	stream := cipher.NewCFBDecrypter(block, iv)
	stream.XORKeyStream(ciphertext, ciphertext)
	return string(ciphertext), nil
}

func Audit(c *gin.Context) {
	_, span := Tracer.Start(c.Request.Context(), "audit")
	defer span.End()

	var req AuditRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	logEntry := fmt.Sprintf("event=%s user_id=%s data=%v", req.Event, req.UserID, req.Data)
	encrypted, err := EncryptAES256(logEntry)
	if err != nil {
		encrypted = "[encryption_error]"
	}
	entry := AuditLogEntry{
		Encrypted: encrypted,
		UserID:    req.UserID,
		Event:     req.Event,
		Timestamp: time.Now().Unix(),
	}
	AuditLogs = append(AuditLogs, entry)
	ExternalAuditStore = append(ExternalAuditStore, entry)
	c.JSON(http.StatusOK, gin.H{"status": "audited", "event": req.Event})
}

func RiskScan(c *gin.Context) {
	_, span := Tracer.Start(c.Request.Context(), "riskScan")
	defer span.End()

	var req RiskScanRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"status": "scanned"})
}

func GetLogs(c *gin.Context) {
	_, span := Tracer.Start(c.Request.Context(), "getLogs")
	defer span.End()

	user := c.Query("user_id")
	event := c.Query("event")
	var filtered []AuditLogEntry
	for _, entry := range AuditLogs {
		if (user == "" || entry.UserID == user) && (event == "" || entry.Event == event) {
			filtered = append(filtered, entry)
		}
	}
	c.JSON(http.StatusOK, gin.H{"logs": filtered})
}

func GetDecryptedLogs(c *gin.Context) {
	adminToken := c.GetHeader("X-Admin-Token")
	if adminToken != "supersecretadmin" {
		c.JSON(http.StatusForbidden, gin.H{"error": "admin access required"})
		return
	}
	user := c.Query("user_id")
	event := c.Query("event")
	var decrypted []string
	for _, entry := range AuditLogs {
		if (user == "" || entry.UserID == user) && (event == "" || entry.Event == event) {
			enc := entry.Encrypted
			if enc == "[encryption_error]" {
				decrypted = append(decrypted, enc)
				continue
			}
			dec, err := DecryptAES256(enc)
			if err != nil {
				decrypted = append(decrypted, "[decryption_error]")
			} else {
				decrypted = append(decrypted, dec)
			}
		}
	}
	c.JSON(http.StatusOK, gin.H{"decrypted_logs": decrypted})
}

func HealthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}
