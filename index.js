const express = require('express');
const app = express();
const port = 3000;
const servoController = new (require('./servo-controller'))();

app.get('/feedit', (req, res) => {
    servoController.feedOnce();
})

app.get('/wiggleit', (req, res) => {
    servoController.wiggler();
})

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`)
})