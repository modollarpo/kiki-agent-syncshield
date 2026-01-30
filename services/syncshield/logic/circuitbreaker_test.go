package logic

import "testing"

type CircuitBreaker struct {
	tripped bool
}

func (cb *CircuitBreaker) Trip()           { cb.tripped = true }
func (cb *CircuitBreaker) Reset()          { cb.tripped = false }
func (cb *CircuitBreaker) IsTripped() bool { return cb.tripped }

func TestCircuitBreaker(t *testing.T) {
	cb := &CircuitBreaker{}
	if cb.IsTripped() {
		t.Error("Should not be tripped initially")
	}
	cb.Trip()
	if !cb.IsTripped() {
		t.Error("Should be tripped after Trip()")
	}
	cb.Reset()
	if cb.IsTripped() {
		t.Error("Should not be tripped after Reset()")
	}
}
