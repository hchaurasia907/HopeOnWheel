const express = require('express');
const { calculateTrip, confirmTrip } = require('../controllers/tripController');
const { protect } = require('../middleware/authMiddleware');
const router = express.Router();

router.post('/calculate', protect, calculateTrip);
router.post('/confirm', protect, confirmTrip);

module.exports = router;
