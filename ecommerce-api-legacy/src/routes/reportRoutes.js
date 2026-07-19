const express = require('express');
const reportController = require('../controllers/reportController');

const router = express.Router();

router.get('/api/admin/financial-report', async (req, res, next) => {
    try {
        const report = await reportController.financialReport();
        res.json(report);
    } catch (err) {
        next(err);
    }
});

module.exports = router;
