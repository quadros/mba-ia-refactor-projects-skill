/**
 * Antes: DELETE /api/users/:id apagava o usuário e deixava matrículas e
 * pagamentos órfãos no banco (reconhecido no próprio texto de resposta
 * original). Agora remove os dados dependentes explicitamente.
 */
const userModel = require('../models/userModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');

async function deleteUser(userId) {
    const enrollments = await enrollmentModel.findByUserId(userId);
    const enrollmentIds = enrollments.map((e) => e.id);

    if (enrollmentIds.length) {
        await paymentModel.deleteByEnrollmentIds(enrollmentIds);
        await enrollmentModel.deleteByUserId(userId);
    }
    await userModel.deleteById(userId);

    return { deletedEnrollments: enrollmentIds.length };
}

module.exports = { deleteUser };
