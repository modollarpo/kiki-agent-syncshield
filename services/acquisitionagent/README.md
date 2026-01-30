# Acquisition Agent Service

## Responsibilities

- Optimise media spend allocation using SyncValue™ outputs

- Replace ROAS logic with predicted LTV
- Support budget constraints, pacing, and scenario simulations

## Architecture

- Clean architecture: domain, app, infrastructure, interfaces, tests

- Service interface consumes SyncValue™ predictions
- Pluggable budget optimisation strategy pattern
- Simulation endpoints for what-if analysis
- Event-driven inputs/outputs
- Decision logic separated from execution adapters

## External Systems

- All ad platform integrations are abstracted (no real API calls)

- All external calls are mocked in tests

## Endpoints

- `/optimise` (POST): Optimise budget allocation

- `/simulate` (POST): Run scenario simulation
- `/healthz` (GET): Health check

## Compliance

- Audit logging, strong typing, docstrings

