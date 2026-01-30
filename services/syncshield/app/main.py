```python
package main

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"golang.org/x/crypto/bcrypt"
	"math/rand"
	"net/http"
	"sync"
	"time"
)

var userDB = map[string]map[string]interface{}{"admin": {"username": "admin", "password": hashPassword("adminpass"), "role": "admin"}}
var emailVerification = map[string]string{}
var passwordReset = map[string]string{}
var auditLog []map[string]interface{}
var secretKey = []byte("supersecretkey")
var tokenExpire = time.Hour
var mu sync.Mutex

func hashPassword(pw string) string {
	b, _ := bcrypt.GenerateFromPassword([]byte(pw), bcrypt.DefaultCost)
	return string(b)
}
func checkPassword(pw, hash string) bool {
	return bcrypt.CompareHashAndPassword([]byte(hash), []byte(pw)) == nil
}
func issueToken(username, role string) (string, error) {
	claims := jwt.MapClaims{"sub": username, "role": role, "exp": time.Now().Add(tokenExpire).Unix()}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(secretKey)
}
func requireRole(role string) gin.HandlerFunc {
	return func(c *gin.Context) {
		tokenStr := c.GetHeader("Authorization")[7:]
		claims := jwt.MapClaims{}
		token, err := jwt.ParseWithClaims(tokenStr, claims, func(token *jwt.Token) (interface{}, error) { return secretKey, nil })
		if err != nil || claims["role"] != role {
			c.AbortWithStatus(http.StatusForbidden)
			return
		}
		c.Set("user", claims["sub"])
		c.Next()
	}
}
func register(c *gin.Context) {
	var req struct{ Username, Password, Role string }
	c.BindJSON(&req)
	mu.Lock()
	if _, exists := userDB[req.Username]; exists {
		c.JSON(http.StatusBadRequest, gin.H{"error": "User exists"})
		mu.Unlock(); return
	}
	userDB[req.Username] = map[string]interface{}{ "username": req.Username, "password": hashPassword(req.Password), "role": req.Role }
	mu.Unlock()
	c.JSON(http.StatusOK, gin.H{"msg": "Registered"})
}
func login(c *gin.Context) {
	var req struct{ Username, Password string }
	c.BindJSON(&req)
	user, exists := userDB[req.Username]
	if !exists || !checkPassword(req.Password, user["password"].(string)) {
		auditLog = append(auditLog, map[string]interface{}{ "user": req.Username, "action": "login_failed", "timestamp": time.Now().Format(time.RFC3339) })
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"}); return
	}
	token, _ := issueToken(req.Username, user["role"].(string))
	auditLog = append(auditLog, map[string]interface{}{ "user": req.Username, "action": "login", "timestamp": time.Now().Format(time.RFC3339) })
	c.JSON(http.StatusOK, gin.H{"access_token": token, "token_type": "bearer"})
}
func profile(c *gin.Context) {
	user := c.GetString("user")
	auditLog = append(auditLog, map[string]interface{}{ "user": user, "action": "view_profile", "timestamp": time.Now().Format(time.RFC3339) })
	c.JSON(http.StatusOK, gin.H{"username": user})
}
func passwordResetRequest(c *gin.Context) {
	var req struct{ Username string }
	c.BindJSON(&req)
	if _, exists := userDB[req.Username]; !exists {
		c.JSON(http.StatusBadRequest, gin.H{"error": "User not found"}); return
	}
	token := fmt.Sprintf("%d", rand.Int())
	passwordReset[req.Username] = token
	c.JSON(http.StatusOK, gin.H{"msg": "Password reset email sent", "token": token})
}
func passwordReset(c *gin.Context) {
	var req struct{ Username, Token, NewPassword string }
	c.BindJSON(&req)
	if passwordReset[req.Username] != req.Token {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid token"}); return
	}
	userDB[req.Username]["password"] = hashPassword(req.NewPassword)
	auditLog = append(auditLog, map[string]interface{}{ "user": req.Username, "action": "password_reset", "timestamp": time.Now().Format(time.RFC3339) })
	c.JSON(http.StatusOK, gin.H{"msg": "Password updated"})
}
func verifyEmail(c *gin.Context) {
	var req struct{ Username string }
	c.BindJSON(&req)
	if _, exists := userDB[req.Username]; !exists {
		c.JSON(http.StatusBadRequest, gin.H{"error": "User not found"}); return
	}
	token := fmt.Sprintf("%d", rand.Int())
	emailVerification[req.Username] = token
	c.JSON(http.StatusOK, gin.H{"msg": "Verification email sent", "token": token})
}
func confirmEmail(c *gin.Context) {
	var req struct{ Username, Token string }
	c.BindJSON(&req)
	if emailVerification[req.Username] != req.Token {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid token"}); return
	}
	userDB[req.Username]["verified"] = true
	auditLog = append(auditLog, map[string]interface{}{ "user": req.Username, "action": "email_verified", "timestamp": time.Now().Format(time.RFC3339) })
	c.JSON(http.StatusOK, gin.H{"msg": "Email verified"})
}
func auditLogHandler(c *gin.Context) {
	c.JSON(http.StatusOK, auditLog)
}

func main() {
	r := gin.Default()
	r.POST("/register", register)
	r.POST("/login", login)
	r.POST("/profile", requireRole("admin"), profile)
	r.POST("/password-reset-request", passwordResetRequest)
	r.POST("/password-reset", passwordReset)
	r.POST("/verify-email", verifyEmail)
	r.POST("/confirm-email", confirmEmail)
	r.GET("/audit-log", requireRole("admin"), auditLogHandler)
	r.Run(":8000")
}
```