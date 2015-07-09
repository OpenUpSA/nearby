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
      $('.btn.locate span').text('Use your location');
      alert('Sorry, your browser was unable to determine your location.');
    }

    if (navigator.geolocation) {
      $('.btn.locate span').text('Locating...');
      navigator.geolocation.getCurrentPosition(foundLocation, noLocation, {timeout:10000});
    } else {
      noLocation();
    }
  });

  var map = new L.Map("map", {
    scrollWheelZoom: false
  });
  map.attributionControl.setPrefix('');
  var osm = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: 'Map © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 18
  });
  map.addLayer(osm);

  var wardId = $('#map').attr('data');

  $.getJSON("http://mapit.code4sa.org/mapit/area/31.geojson").
      then(function(data) {
          var area = new L.GeoJSON(data);
          map.addLayer(area);
          map.fitBounds(area.getBounds());
      });
});

$(function() {
  $('#suggest-modal form').on('submit', function(e) {
    e.preventDefault();

    var $form = $(e.target);
    $.post($form.attr('action'), $form.serialize());
    $('#suggest-modal').modal('hide');
    alert("Thanks for your suggestion, we'll take a look and update our data.");
  });
});
