package shared

import (
	"fmt"
	"kiki_agent/schemas"
	"kiki_agent/utils"
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
