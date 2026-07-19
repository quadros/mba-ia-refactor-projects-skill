/**
 * Substitui `globalCache` (variável de módulo mutável compartilhada por
 * todas as requisições) por um serviço com estado encapsulado, exportado
 * como singleton explícito — testável e substituível, ao contrário de
 * uma variável solta.
 */
class CacheService {
    constructor() {
        this._store = new Map();
    }

    set(key, value) {
        this._store.set(key, value);
    }

    get(key) {
        return this._store.get(key);
    }
}

module.exports = new CacheService();
