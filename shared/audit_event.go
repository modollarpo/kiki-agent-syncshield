package shared

type AuditEvent struct {
	Event  string                 `json:"event"`
	UserID string                 `json:"user_id"`
	Data   map[string]interface{} `json:"data"`
}
