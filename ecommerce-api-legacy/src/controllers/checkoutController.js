/**
 * Orquestra o caso de uso de checkout. Antes vivia inline dentro da rota
 * Express, como uma pirâmide de callbacks (ver AppManager.js original).
 */
const userModel = require('../models/userModel');
const courseModel = require('../models/courseModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');
const auditModel = require('../models/auditModel');
const paymentService = require('../services/paymentService');
const cacheService = require('../services/cacheService');
const { HttpError } = require('../middlewares/httpError');

async function checkout({ userName, email, password, courseId, cardNumber }) {
    if (!userName || !email || !courseId || !cardNumber) {
        throw new HttpError(400, 'Bad Request');
    }

    const course = await courseModel.findActiveById(courseId);
    if (!course) throw new HttpError(404, 'Curso não encontrado');

    let user = await userModel.findByEmail(email);
    if (!user) {
        user = await userModel.create({ name: userName, email, password });
    }

    const paymentResult = paymentService.charge(cardNumber, course.price);
    if (!paymentResult.approved) throw new HttpError(400, 'Pagamento recusado');

    const enrollment = await enrollmentModel.create(user.id, courseId);
    await paymentModel.create(enrollment.id, course.price, paymentResult.status);
    await auditModel.log(`Checkout curso ${courseId} por ${user.id}`);

    cacheService.set(`last_checkout_${user.id}`, course.title);

    return { enrollmentId: enrollment.id };
}

module.exports = { checkout };
