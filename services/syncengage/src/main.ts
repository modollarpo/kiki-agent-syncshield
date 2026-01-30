import 'reflect-metadata';
// SyncEngage Service – KIKI Agent™
// CRM Automation (NestJS, BullMQ, Redis, CRM connectors)
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.setGlobalPrefix('api');
  await app.listen(process.env.PORT || 8085);
}

bootstrap();
