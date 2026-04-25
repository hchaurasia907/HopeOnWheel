const User = require('../models/User');
const Trip = require('../models/Trip');
const Transaction = require('../models/Transaction');

const PRICE_PER_KM = 10; // ₹10/km

// @desc    Calculate Trip Cost
// @route   POST /api/trip/calculate
// @access  Private
exports.calculateTrip = async (req, res) => {
    const { source, destination } = req.body;

    if (!source || !destination) {
        return res.status(400).json({ message: 'Source and destination are required' });
    }

    // Simulate distance calculation (random between 5 and 50 km for this mock)
    // In a real app, integrate with Google Maps Distance Matrix API
    const simulatedDistance = Math.floor(Math.random() * 45) + 5; 
    const estimatedCost = simulatedDistance * PRICE_PER_KM;

    res.json({
        source,
        destination,
        distance: simulatedDistance,
        estimatedCost
    });
};

// @desc    Confirm Trip & Deduct Wallet
// @route   POST /api/trip/confirm
// @access  Private
exports.confirmTrip = async (req, res) => {
    const { distance, cost } = req.body;

    if (!distance || !cost) {
        return res.status(400).json({ message: 'Distance and cost are required' });
    }

    try {
        const user = await User.findById(req.user._id);

        if (user.walletBalance < cost) {
            return res.status(400).json({ message: 'Insufficient wallet balance' });
        }

        // Deduct from wallet
        user.walletBalance -= cost;
        await user.save();

        // Record transaction
        const transaction = new Transaction({
            userId: user._id,
            amount: cost,
            type: 'debit'
        });
        await transaction.save();

        // Record trip
        const trip = new Trip({
            userId: user._id,
            distance,
            cost
        });
        const savedTrip = await trip.save();

        res.status(201).json({
            message: 'Trip confirmed successfully',
            trip: savedTrip,
            newBalance: user.walletBalance
        });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};
