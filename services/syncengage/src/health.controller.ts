// Health check controller for SyncEngage
import { Controller, Get } from '@nestjs/common';

@Controller('healthz')
export class HealthController {
  @Get()
  healthz() {
    return { status: 'ok' };
  }
}
