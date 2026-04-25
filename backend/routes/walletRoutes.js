const express = require('express');
const { getWallet, addMoney } = require('../controllers/walletController');
const { protect } = require('../middleware/authMiddleware');
const router = express.Router();

router.route('/').get(protect, getWallet);
router.route('/add-money').post(protect, addMoney);

module.exports = router;
