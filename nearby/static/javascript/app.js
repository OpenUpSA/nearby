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
