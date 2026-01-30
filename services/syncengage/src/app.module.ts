// AppModule for SyncEngage (NestJS)
import { Module } from '@nestjs/common';
import { BullModule } from '@nestjs/bullmq';
import { RedisModule } from './redis.module';
import { HealthController } from './health.controller';
import { RetentionController } from './retention.controller';
import { RetentionSwitchboardService } from './retention_switchboard.service';

@Module({
  imports: [
    BullModule.forRoot({
      connection: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379'),
      },
    }),
    RedisModule,
  ],
  controllers: [HealthController, RetentionController],
  providers: [RetentionSwitchboardService],
})
export class AppModule {}
