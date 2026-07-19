/**
 * Hashing de senha com scrypt (módulo nativo `crypto`, sem dependência
 * externa). Substitui `badCrypto`, que era base64 repetido e trivialmente
 * reversível.
 */
const crypto = require('crypto');

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.scryptSync(password, salt, 64).toString('hex');
    return `${salt}:${hash}`;
}

function verifyPassword(password, storedHash) {
    const [salt, hash] = storedHash.split(':');
    const hashBuffer = Buffer.from(hash, 'hex');
    const suppliedBuffer = crypto.scryptSync(password, salt, 64);
    return crypto.timingSafeEqual(hashBuffer, suppliedBuffer);
}

module.exports = { hashPassword, verifyPassword };
