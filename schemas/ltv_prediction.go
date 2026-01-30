package schemas

type LTVPredictionRequest struct {
	UserID   string                 `json:"user_id"`
	Features map[string]interface{} `json:"features"`
}

type LTVPredictionResponse struct {
	LTV    float64 `json:"ltv"`
	UserID string  `json:"user_id"`
}
