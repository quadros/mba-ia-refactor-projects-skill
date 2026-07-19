/**
 * Configuração centralizada, lida de variáveis de ambiente.
 * Nenhum segredo real deve viver aqui como literal.
 */
const settings = {
    dbPath: process.env.DB_PATH || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || 'pk_test_dev_only',
    smtpUser: process.env.SMTP_USER || 'no-reply@example.com',
    port: parseInt(process.env.PORT || '3000', 10),
};

module.exports = { settings };
