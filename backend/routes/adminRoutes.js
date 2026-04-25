const express = require('express');
const { getUsers, updateUser, deleteUser, toggleBlockUser } = require('../controllers/adminController');
const { protect, admin } = require('../middleware/authMiddleware');
const router = express.Router();

router.route('/users').get(protect, admin, getUsers);
router.route('/users/:id')
    .put(protect, admin, updateUser)
    .delete(protect, admin, deleteUser);
    
router.patch('/users/:id/block', protect, admin, toggleBlockUser);

module.exports = router;
