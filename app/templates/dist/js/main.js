'use strict';

// DOM!
const localVideo = document.querySelector('video');

const contraintes = {
	video: true,
	audio: false,
};

function obtenuMedia(fluxMedia) {
	localVideo.srcObject = fluxMedia;
	console.log("réussi à capturer les flux!");

};

function errorMedia(erreur) {
	console.log("avoir une erreur pour le flux =(");
}; 

navigator.mediaDevices.getUserMedia(contraintes).then(obtenuMedia).catch(errorMedia);