const express = require('express');
const userController = require('../controllers/userController');

const router = express.Router();

router.delete('/api/users/:id', async (req, res, next) => {
    try {
        const result = await userController.deleteUser(req.params.id);
        res.json({ mensagem: 'Usuário e dados relacionados removidos com sucesso', ...result });
    } catch (err) {
        next(err);
    }
});

module.exports = router;
