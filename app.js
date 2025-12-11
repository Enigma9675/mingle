const express = require('express');
const app = express();
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
require('dotenv/config');

app.use(bodyParser.json());

const authRoute = require('./routes/auth');
const postsRoute = require('./routes/posts');

app.use('/api/user', authRoute);
app.use('/api/posts', postsRoute);

mongoose.connect(process.env.DB_CONNECTOR)
    .then(() => console.log('Connected to DB!'));

app.listen(3000, () => console.log('Server running on 3000'));