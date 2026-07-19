const express = require('express');
const checkoutController = require('../controllers/checkoutController');

const router = express.Router();

router.post('/api/checkout', async (req, res, next) => {
    try {
        const { usr: userName, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body;
        const result = await checkoutController.checkout({ userName, email, password, courseId, cardNumber });
        res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
    } catch (err) {
        next(err);
    }
});

module.exports = router;
