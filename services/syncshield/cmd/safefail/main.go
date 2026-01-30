package main

import (
	"context"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	safefail "kiki-agent-syncshield/safefail"
)

func main() {
	guard := &safefail.SafeFailGuard{
		ReflexEndpoint: "syncreflex:50058",
		RollbackFunc:   safefail.RollbackAll,
		ThresholdDrop:  -0.15,
		ThresholdNeg:   10,
	}
	logger, err := safefail.NewAuditLogger("/app/audit.log")
	if err != nil {
		log.Fatalf("Failed to open audit log: %v", err)
	}
	defer logger.Close()
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	go guard.Monitor(ctx)
	safefail.StartRESTAndGRPC(guard)
	// Graceful shutdown
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	<-c
	log.Println("[SafeFail] Shutting down...")
	cancel()
	time.Sleep(1 * time.Second)
}
