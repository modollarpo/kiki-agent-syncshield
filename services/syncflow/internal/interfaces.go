package internal

type BiddingService interface {
	ExecuteBid(userID string, adSlot string, bidAmount float64) (bidID string, accepted bool, reason string)
}
