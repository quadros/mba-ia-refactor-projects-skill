const db = require('../db/database');

async function create(userId, courseId) {
    const { lastID } = await db.run(
        'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
        [userId, courseId]
    );
    return { id: lastID, userId, courseId };
}

async function findByUserId(userId) {
    return db.all('SELECT * FROM enrollments WHERE user_id = ?', [userId]);
}

async function deleteByUserId(userId) {
    await db.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
}

module.exports = { create, findByUserId, deleteByUserId };
