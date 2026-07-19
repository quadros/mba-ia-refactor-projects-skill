const db = require('../db/database');

async function create(enrollmentId, amount, status) {
    const { lastID } = await db.run(
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [enrollmentId, amount, status]
    );
    return { id: lastID, enrollmentId, amount, status };
}

async function deleteByEnrollmentIds(enrollmentIds) {
    if (!enrollmentIds.length) return;
    const placeholders = enrollmentIds.map(() => '?').join(', ');
    await db.run(`DELETE FROM payments WHERE enrollment_id IN (${placeholders})`, enrollmentIds);
}

module.exports = { create, deleteByEnrollmentIds };
