const mongoose = require('mongoose');

const feedbackSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        required: true,
        ref: 'User',
    },
    rating: {
        type: Number,
        required: true,
        min: 1,
        max: 5,
    },
    message: {
        type: String,
        required: true,
    }
}, { timestamps: true });

module.exports = mongoose.model('Feedback', feedbackSchema);
