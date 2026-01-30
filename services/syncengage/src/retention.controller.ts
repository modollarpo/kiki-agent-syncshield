import { Controller, Post, Body } from '@nestjs/common';
import { RetentionSwitchboardService } from './retention_switchboard.service';

@Controller('retention')
export class RetentionController {
  constructor(private readonly switchboard: RetentionSwitchboardService) {}

  @Post('trigger')
  async trigger(@Body() body: any) {
    // body: { event: string, user: string, data: any }
    return this.switchboard.routeEvent(body.event, body.user, body.data);
  }
}
