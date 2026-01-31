package shared

import (
	"fmt"
	"kiki-agent-syncshield/schemas"
	"kiki-agent-syncshield/utils"
	// TODO: Update to correct module path for utils or use relative import if appropriate.
)

func ExampleUsage() {
	user := schemas.User{ID: "u1", Email: "test@example.com", Name: "Test User", IsActive: true}
	errors := utils.ValidateStruct(user)
	if len(errors) > 0 {
		fmt.Println("Validation failed:", errors)
	} else {
		fmt.Println("User valid:", user)
	}
	event := AuditEvent{Event: "login", UserID: user.ID, Data: map[string]interface{}{"ip": "127.0.0.1"}}
	fmt.Printf("Audit event: %+v\n", event)
}
