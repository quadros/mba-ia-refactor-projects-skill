const db = require('../db/database');

async function findActiveById(id) {
    return db.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
}

async function findAll() {
    return db.all('SELECT * FROM courses');
}

module.exports = { findActiveById, findAll };
