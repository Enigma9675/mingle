const express = require('express');
const router = express.Router();
const User = require('../models/User');
const { registerValidation, loginValidation } = require('./validation'); 
const bcryptjs = require('bcryptjs');
const jwt = require('jsonwebtoken');

// REGISTER ROUTE
router.post('/register', async (req, res) => {
    // 1. Validate user input
    const { error } = registerValidation(req.body);
    if (error) return res.status(400).send({ message: error.details[0].message });

    // 2. Check if the user already exists
    const emailExists = await User.findOne({ email: req.body.email });
    if (emailExists) return res.status(400).send({ message: 'Email already exists' });

    // 3. Hash the password
    const salt = await bcryptjs.genSalt(10);
    const hashedPassword = await bcryptjs.hash(req.body.password, salt);

    // 4. Create a new user
    const user = new User({
        username: req.body.username,
        email: req.body.email,
        password: hashedPassword
    });

    try {
        const savedUser = await user.save();
        res.send({ userId: savedUser._id, username: savedUser.username });
    } catch (err) {
        res.status(400).send({ message: err });
    }
});

// LOGIN ROUTE
router.post('/login', async (req, res) => {
    // 1. Validate user input
    const { error } = loginValidation(req.body);
    if (error) return res.status(400).send({ message: error.details[0].message });

    // 2. Check if the email exists
    const user = await User.findOne({ email: req.body.email });
    if (!user) return res.status(400).send({ message: 'User does not exist' });

    // 3. Check if password is correct
    const validPass = await bcryptjs.compare(req.body.password, user.password);
    if (!validPass) return res.status(400).send({ message: 'Invalid password' });

    // 4. Create and assign a token
    const token = jwt.sign({ _id: user._id, username: user.username }, process.env.TOKEN_SECRET);
    res.header('auth-token', token).send({ 'auth-token': token });
});

module.exports = router;