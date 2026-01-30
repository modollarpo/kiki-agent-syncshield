package schemas

type BidRequest struct {
	UserID    string  `json:"user_id"`
	AdSlot    string  `json:"ad_slot"`
	BidAmount float64 `json:"bid_amount"`
}

type BidResponse struct {
	BidID    string `json:"bid_id"`
	Accepted bool   `json:"accepted"`
	Reason   string `json:"reason,omitempty"`
}
