const mongoose = require('mongoose');

const transactionSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        required: true,
        ref: 'User',
    },
    amount: {
        type: Number,
        required: true,
    },
    type: {
        type: String,
        enum: ['credit', 'debit'],
        required: true,
    }
}, { timestamps: true });

module.exports = mongoose.model('Transaction', transactionSchema);
