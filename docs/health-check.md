# Health Check Configuration

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /health | GET | Basic health check |
| /health/ready | GET | Readiness probe |
| /health/live | GET | Liveness probe |
| /health/startup | GET | Startup probe |

## Configuration

`yaml
health:
  check_interval: 30s
  timeout: 5s
  failure_threshold: 3
  success_threshold: 1
`

## Dependencies Checked
- Database connectivity
- Redis connectivity  
- SMS gateway API reachability
- Message queue health

> Last updated: 2026-02-14