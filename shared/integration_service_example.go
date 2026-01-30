package shared

import (
	"bytes"
	"encoding/json"
	"fmt"
	"kiki_agent/schemas"
	"net/http"
)

func CallSyncflowBid() {
	bidReq := schemas.BidRequest{UserID: "u1", AdSlot: "banner_top", BidAmount: 1.23}
	body, _ := json.Marshal(bidReq)
	resp, err := http.Post("http://syncflow:8000/execute-bid", "application/json", bytes.NewReader(body))
	if err != nil {
		fmt.Println("Bid call failed:", err)
		return
	}
	defer resp.Body.Close()
	var bidResp schemas.BidResponse
	if err := json.NewDecoder(resp.Body).Decode(&bidResp); err == nil {
		fmt.Printf("BidResponse: %+v\n", bidResp)
	} else {
		fmt.Println("Bid decode failed:", err)
	}
}

func CallSyncvalueLTV() {
	ltvReq := schemas.LTVPredictionRequest{UserID: "u1", Features: map[string]interface{}{"f1": 1.0}}
	body, _ := json.Marshal(ltvReq)
	resp, err := http.Post("http://syncvalue:8000/predict-ltv", "application/json", bytes.NewReader(body))
	if err != nil {
		fmt.Println("LTV call failed:", err)
		return
	}
	defer resp.Body.Close()
	var ltvResp schemas.LTVPredictionResponse
	if err := json.NewDecoder(resp.Body).Decode(&ltvResp); err == nil {
		fmt.Printf("LTVPredictionResponse: %+v\n", ltvResp)
	} else {
		fmt.Println("LTV decode failed:", err)
	}
}
