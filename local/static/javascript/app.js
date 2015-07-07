$(function() {
  $('.btn.locate').on('click', function(e) {
    // find user's location
    e.preventDefault();

    function foundLocation(position) {
      lat = position.coords.latitude;
      lng = position.coords.longitude;
      window.location = '/councillor?lat=' + lat + '&lng=' + lng;
    }

    function noLocation() {
        alert('Sorry, your browser was unable to determine your location.');
    }

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(foundLocation, noLocation, {timeout:10000});
    } else {
      noLocation();
    }
  });
});
