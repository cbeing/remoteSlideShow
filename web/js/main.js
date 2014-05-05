/**
 * This file is under MIT License
 * Copyright (C) 2014 Skander Ben Mahmoud <skander.benmahmoud@esprit.tn>
 *   
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *   
 * The above copyright notice and this permission notice shall be included in all copies
 * or substantial portions of the Software.
 *   
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
 * AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 * DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 * ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/


// Global vars that we need everywhere !!
var fContent; // The file content.
var fSize = 0;
var fName = "";

function readFile(e) {
  var f = e.target.files[0];
  if(f){

    fSize = f.size;
    fName = f.name;

    var reader = new FileReader();
    reader.onload = function (evt){
      fContent = evt.target.result;
    }

    reader.readAsArrayBuffer(f); // Keeping the integrity of data.
  }
}


// websocket :
var server;
var ws;

function connect(){
 server = document.getElementById('ip').value;
 ws = new WebSocket("ws://"+server+":9000/");

 ws.onerror = function (){
   console.error("Couldon't connect to :"+server);
 }

 ws.onopen = function (){
   console.log('Connected to :'+server);
 }
}


function openSlide(){
  ws.send('OPEN');
}

function closeSlide(){
  ws.send('EXIT');
}

function nextSlide(){
  ws.send('NEXT');
}

function backSlide(){
  ws.send('BACK');
}

function captureNote() {
  ws.send('CAPT');
}

function saveNotes() {
  ws.send('SAVENOTES');
}

function sendFile(){
  /*
   * Actually, we will send two different messages,
   * The first one is the header, that contains the |SEND| command and
   * the filename.
   * Then we send the data, which is the content of the file.
   * We are sending separetely because javascript does not allow us to mix-up
   * text fomat and binary format. Otherwise, the data will be corrupted.
   */

  var frame_header = "SEND:" + fName ;
  var frame_data = fContent;

  ws.send(frame_header); // First we send the header.

  ws.send(fContent);  // Then we send the data.
  console.log("Finished sending stuff...");

}
