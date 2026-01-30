//go:build wireinject
// +build wireinject

package app

import (
	"kiki_agent/services/syncshield/internal"

	"github.com/google/wire"
)

func InitializeComplianceService() internal.ComplianceService {
	wire.Build(internal.NewComplianceService)
	return nil
}
