const mongoose = require('mongoose');

const tripSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        required: true,
        ref: 'User',
    },
    distance: {
        type: Number, // in kilometers
        required: true,
    },
    cost: {
        type: Number,
        required: true,
    }
}, { timestamps: true });

module.exports = mongoose.model('Trip', tripSchema);
