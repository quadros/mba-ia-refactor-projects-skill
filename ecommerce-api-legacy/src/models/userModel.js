const db = require('../db/database');
const { hashPassword } = require('../services/authService');

async function findByEmail(email) {
    return db.get('SELECT * FROM users WHERE email = ?', [email]);
}

async function create({ name, email, password }) {
    const passwordHash = await hashPassword(password || '123456');
    const { lastID } = await db.run(
        'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        [name, email, passwordHash]
    );
    return { id: lastID, name, email };
}

async function deleteById(id) {
    await db.run('DELETE FROM users WHERE id = ?', [id]);
}

module.exports = { findByEmail, create, deleteById };
