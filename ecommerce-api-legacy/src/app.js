/**
 * Composition root: monta a aplicação Express. Nenhuma regra de negócio
 * mora aqui — apenas configuração, registro de rotas e middlewares.
 */
const express = require('express');
const { settings } = require('./config/settings');
const database = require('./db/database');
const { errorHandler } = require('./middlewares/errorHandler');
const checkoutRoutes = require('./routes/checkoutRoutes');
const reportRoutes = require('./routes/reportRoutes');
const userRoutes = require('./routes/userRoutes');

async function createApp() {
    await database.initSchema();
    await database.seed();

    const app = express();
    app.use(express.json());

    app.use(checkoutRoutes);
    app.use(reportRoutes);
    app.use(userRoutes);

    app.use(errorHandler);

    return app;
}

if (require.main === module) {
    createApp().then((app) => {
        app.listen(settings.port, () => {
            console.log(`LMS API rodando na porta ${settings.port}...`);
        });
    });
}

module.exports = { createApp };
