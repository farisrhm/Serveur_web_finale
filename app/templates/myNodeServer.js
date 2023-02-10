const express = require('express');
const app = express();
const path = require('path');
const router = express.Router();


app.get('/js/main.js', function(req, res) {
    res.sendFile(path.join(__dirname + '/js/main.js'));
});

app.get('/',function(req,res){
  res.sendFile(path.join(__dirname+'/indextele.html'));
  //__dirname : It will resolve to your project folder.
});

//add the router
//app.use('/', router);
app.listen(process.env.port || 8000);

console.log('Running at Port 8000');
