const express = require('express');
const { submitFeedback, getFeedback } = require('../controllers/feedbackController');
const { protect, admin } = require('../middleware/authMiddleware');
const router = express.Router();

router.route('/')
    .post(protect, submitFeedback)
    .get(protect, admin, getFeedback);

module.exports = router;
