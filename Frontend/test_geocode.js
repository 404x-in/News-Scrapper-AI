fetch('https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=19.0760&longitude=72.8777&localityLanguage=en')
  .then(res => res.json())
  .then(console.log);
