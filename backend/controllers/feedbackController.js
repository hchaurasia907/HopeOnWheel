const Feedback = require('../models/Feedback');

// @desc    Submit feedback
// @route   POST /api/feedback
// @access  Private
exports.submitFeedback = async (req, res) => {
    const { rating, message } = req.body;

    try {
        const feedback = new Feedback({
            userId: req.user._id,
            rating,
            message
        });

        const savedFeedback = await feedback.save();
        res.status(201).json(savedFeedback);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// @desc    Get all feedback
// @route   GET /api/feedback
// @access  Private/Admin
exports.getFeedback = async (req, res) => {
    try {
        const feedbacks = await Feedback.find({}).populate('userId', 'name email').sort({ createdAt: -1 });
        res.json(feedbacks);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};
