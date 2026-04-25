const User = require('../models/User');
const Transaction = require('../models/Transaction');

// @desc    Get wallet balance & history
// @route   GET /api/wallet
// @access  Private
exports.getWallet = async (req, res) => {
    try {
        const user = await User.findById(req.user._id);
        const transactions = await Transaction.find({ userId: req.user._id }).sort({ createdAt: -1 });

        res.json({
            balance: user.walletBalance,
            transactions
        });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// @desc    Add money to wallet
// @route   POST /api/wallet/add-money
// @access  Private
exports.addMoney = async (req, res) => {
    const { amount } = req.body;

    if (!amount || amount <= 0) {
        return res.status(400).json({ message: 'Invalid amount' });
    }

    try {
        const user = await User.findById(req.user._id);
        
        user.walletBalance += Number(amount);
        await user.save();

        const transaction = new Transaction({
            userId: user._id,
            amount: Number(amount),
            type: 'credit'
        });
        await transaction.save();

        res.json({
            message: 'Money added successfully',
            balance: user.walletBalance,
            transaction
        });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};
