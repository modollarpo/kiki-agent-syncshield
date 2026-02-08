//go:build wireinject
// +build wireinject

package app

import (
	"kiki_agent/services/kiki-agent-syncflow/internal"

	"github.com/google/wire"
)

func InitializeBiddingService() internal.BiddingService {
	wire.Build(internal.NewBiddingService)
	return nil
}
