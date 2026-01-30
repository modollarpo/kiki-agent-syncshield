package shared

import (
	"fmt"

	"kiki_agent/schemas"
)

func DeepIntegrationExample() {
	// LTV Prediction
	ltvReq := schemas.LTVPredictionRequest{UserID: "u1", Features: map[string]interface{}{"f1": 1.0, "f2": 2.0}}
	fmt.Printf("LTVPredictionRequest: %+v\n", ltvReq)
	ltvResp := schemas.LTVPredictionResponse{LTV: 123.45, UserID: "u1"}
	fmt.Printf("LTVPredictionResponse: %+v\n", ltvResp)
	// Creative
	img := "https://img.url"
	brand := "safe"
	creative := schemas.Creative{CreativeID: "c1", Prompt: "banner", Variant: "default", UserID: "u1", ImageURL: &img, BrandSafety: &brand, Ratings: []int{5, 4, 5}}
	fmt.Printf("Creative: %+v\n", creative)
	// AuditEvent
	event := AuditEvent{Event: "creative_generated", UserID: "u1", Data: map[string]interface{}{"creative_id": creative.CreativeID}}
	fmt.Printf("AuditEvent: %+v\n", event)
}
