"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
// SyncEngage Service – KIKI Agent™
// CRM Automation (NestJS, BullMQ, Redis, CRM connectors)
const core_1 = require("@nestjs/core");
const app_module_1 = require("./app.module");
async function bootstrap() {
    const app = await core_1.NestFactory.create(app_module_1.AppModule);
    app.setGlobalPrefix('api');
    await app.listen(process.env.PORT || 8085);
}
bootstrap();
