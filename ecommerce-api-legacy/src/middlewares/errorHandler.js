/**
 * Tratamento de erro centralizado. Substitui os `res.status(...).send(...)`
 * espalhados em cada rota do código legado — rotas agora só chamam
 * `next(err)` e este middleware decide o status/formato da resposta.
 */
function errorHandler(err, req, res, next) { // eslint-disable-line no-unused-vars
    if (err.status) {
        return res.status(err.status).json({ erro: err.message });
    }
    console.error('Erro não tratado:', err);
    return res.status(500).json({ erro: 'Erro interno do servidor' });
}

module.exports = { errorHandler };
