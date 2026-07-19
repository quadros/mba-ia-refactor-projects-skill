/**
 * Conexão SQLite promisificada. Nenhum model chama sqlite3 diretamente —
 * todos usam run/get/all daqui, com queries sempre parametrizadas.
 */
const sqlite3 = require('sqlite3').verbose();
const { settings } = require('../config/settings');
const { hashPassword } = require('../services/authService');

const db = new sqlite3.Database(settings.dbPath);

function run(sql, params = []) {
    return new Promise((resolve, reject) => {
        db.run(sql, params, function callback(err) {
            if (err) return reject(err);
            resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
}

function get(sql, params = []) {
    return new Promise((resolve, reject) => {
        db.get(sql, params, (err, row) => {
            if (err) return reject(err);
            resolve(row);
        });
    });
}

function all(sql, params = []) {
    return new Promise((resolve, reject) => {
        db.all(sql, params, (err, rows) => {
            if (err) return reject(err);
            resolve(rows);
        });
    });
}

async function initSchema() {
    await run('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)');
    await run('CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
    await run('CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
    await run('CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
    await run('CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');
}

async function seed() {
    const existing = await get('SELECT COUNT(*) as total FROM users');
    if (existing.total > 0) return;

    const passwordHash = await hashPassword('123');
    const { lastID: userId } = await run(
        'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        ['Leonan', 'leonan@fullcycle.com.br', passwordHash]
    );

    const { lastID: courseAId } = await run(
        'INSERT INTO courses (title, price, active) VALUES (?, ?, 1)',
        ['Clean Architecture', 997.0]
    );
    await run('INSERT INTO courses (title, price, active) VALUES (?, ?, 1)', ['Docker', 497.0]);

    const { lastID: enrollmentId } = await run(
        'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
        [userId, courseAId]
    );
    await run(
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [enrollmentId, 997.0, 'PAID']
    );
}

module.exports = { run, get, all, initSchema, seed };
