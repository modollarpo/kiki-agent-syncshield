package internal

type ComplianceService interface {
	Audit(event string, userID string, details map[string]interface{}) error
}
