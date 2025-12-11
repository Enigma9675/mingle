const express = require('express');
const router = express.Router();
const Post = require('../models/post');
const verify = require('../middleware/verifyToken');

// Action 2: Post a message
router.post('/', verify, async (req, res) => {
    // Basic expiration logic: current time + user provided minutes
    const expiration = new Date(Date.now() + (req.body.expirationMinutes * 60000));

    const post = new Post({
        title: req.body.title,
        topic: req.body.topic,
        body: req.body.body,
        expirationTime: expiration,
        owner: req.user._id // Taken from the JWT token
    });

    try {
        const savedPost = await post.save();
        res.json(savedPost);
    } catch (err) {
        res.json({ message: err });
    }
});

// Action 3: Browse messages per topic
router.get('/:topic', verify, async (req, res) => {
    try {
        const posts = await Post.find({ topic: req.params.topic });
        res.json(posts);
    } catch (err) {
        res.json({ message: err });
    }
});

// Action 4: Interact (Like/Dislike/Comment)
router.patch('/:postId/interact', verify, async (req, res) => {
    try {
        const post = await Post.findById(req.params.postId);
        
        // Check Expiration
        if (new Date() > post.expirationTime) {
            return res.status(403).json({ message: "Post Expired" });
        }

        // Apply Logic (Example: Like)
        if (req.body.action === 'like') {
            post.likes += 1;
        } else if (req.body.action === 'comment') {
            post.comments.push({ user: req.user._id, text: req.body.text });
        }
        
        const updatedPost = await post.save();
        res.json(updatedPost);
    } catch (err) {
        res.json({ message: err });
    }
});

module.exports = router;