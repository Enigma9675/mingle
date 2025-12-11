const mongoose = require('mongoose');

const PostSchema = mongoose.Schema({
    title: { type: String, required: true },
    topic: { 
        type: String, 
        required: true, 
        enum: ['Politics', 'Health', 'Sport', 'Tech'] 
    },
    timestamp: { type: Date, default: Date.now },
    body: { type: String, required: true },
    expirationTime: { type: Date, required: true },
    status: { type: String, default: 'Live', enum: ['Live', 'Expired'] },
    owner: { type: String, required: true }, // Stores the Username
    likes: { type: Number, default: 0 },
    dislikes: { type: Number, default: 0 },
    comments: [{
        user: String,
        text: String,
        timestamp: { type: Date, default: Date.now }
    }]
});

module.exports = mongoose.model('Post', PostSchema);