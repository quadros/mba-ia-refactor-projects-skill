/**
 * Gateway de pagamento simulado (mock, sem integração real). Mantém a
 * mesma regra de aprovação do código legado (cartão começando com "4" é
 * aprovado) para não mudar o comportamento observável do checkout, mas
 * agora valida o formato do número antes de decidir e nunca loga o
 * número do cartão nem a chave do gateway.
 */
function isValidCardFormat(cardNumber) {
    return typeof cardNumber === 'string' && /^\d{13,19}$/.test(cardNumber);
}

function charge(cardNumber, amount) {
    if (!isValidCardFormat(cardNumber)) {
        return { approved: false, status: 'INVALID_CARD' };
    }
    const status = cardNumber.startsWith('4') ? 'PAID' : 'DENIED';
    return { approved: status === 'PAID', status, amount };
}

module.exports = { charge, isValidCardFormat };
